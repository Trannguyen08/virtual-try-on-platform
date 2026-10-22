"""Persistence and failure cases for the M3 database layer."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from fastapi.testclient import TestClient
from sqlalchemy import inspect

from backend.core.config import Settings
from backend.db.models import Base, JobRecord
from backend.db.repository import AssetRepository, BodyRepository, JobRepository
from backend.db.session import make_engine, make_session_factory
from backend.main import create_app


def test_schema_migration_tc_api_08(tmp_path, monkeypatch):
    """Test Case ID: TC-API-08. Alembic creates five metadata tables."""
    url = f"sqlite+pysqlite:///{(tmp_path / 'migration.sqlite3').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    config = Config(str(Path(__file__).resolve().parents[3] / "alembic.ini"))
    command.upgrade(config, "head")
    engine = make_engine(url)
    assert {"bodies", "assets", "tryon_jobs", "job_steps", "image_tryon_jobs"} <= set(
        inspect(engine).get_table_names()
    )
    with engine.connect() as connection:
        assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []
    engine.dispose()


def test_job_and_assets_survive_app_restart_tc_api_08(tmp_path, png_bytes, monkeypatch):
    """Test Case ID: TC-API-08. Job, body and GLB remain readable after restart."""
    url = f"sqlite+pysqlite:///{(tmp_path / 'restart.sqlite3').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    engine = make_engine(url)
    Base.metadata.create_all(engine)
    engine.dispose()
    settings = Settings(database_url=url)
    with TestClient(create_app(settings)) as first:
        body = first.post("/api/tryon/analyze", data={"height_cm": "170"},
                          files={"image": ("x.png", png_bytes, "image/png")}).json()["data"]
        created = first.post("/api/tryon/fit", json={
            "body_id": body["body_id"], "garment_id": "demo-tshirt", "size": "M",
        }).json()["data"]
        asset_bytes = first.get("/api/assets/mock-body.glb").content
    with TestClient(create_app(settings)) as restarted:
        response = restarted.get(f"/api/jobs/{created['job_id']}")
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "completed"
        assert restarted.get("/api/assets/mock-body.glb").content == asset_bytes
        assert restarted.post("/api/tryon/fit", json={
            "body_id": body["body_id"], "garment_id": "demo-tshirt", "size": "L",
        }).status_code == 202
        jobs = restarted.app.state.orchestrator.jobs.repository
        assert [job.job_id for job in jobs.list(body_id=body["body_id"], status="completed")]
        with jobs.sessions() as session:
            stored = session.get(JobRecord, created["job_id"])
            assert stored.body_id == body["body_id"]
            assert stored.started_at is not None and stored.finished_at is not None
            assert stored.duration_ms >= 0
        assert [(step.step, step.status) for step in jobs.steps(created["job_id"])] == [
            ("request_accepted", "completed"), ("fit", "completed"),
        ]
        assert jobs.steps(created["job_id"])[1].duration_ms >= 0
        assert jobs.log_step(created["job_id"], "asset_audit", "completed").step == "asset_audit"
    # A fresh interpreter verifies that no process-local store is required.
    script = """
import hashlib
import json
import sys
from fastapi.testclient import TestClient
from backend.core.config import Settings
from backend.main import create_app

with TestClient(create_app(Settings(database_url=sys.argv[1]))) as client:
    job = client.get('/api/jobs/' + sys.argv[2])
    asset = client.get('/api/assets/mock-body.glb')
    print(json.dumps({
        'job_status': job.json()['data']['status'],
        'asset_status': asset.status_code,
        'asset_sha256': hashlib.sha256(asset.content).hexdigest(),
    }))
"""
    process = subprocess.run(
        [sys.executable, "-c", script, url, created["job_id"]],
        cwd=Path(__file__).resolve().parents[3], capture_output=True, text=True,
        timeout=30, check=False,
    )
    assert process.returncode == 0, process.stderr
    observed = json.loads(process.stdout)
    assert observed == {
        "job_status": "completed", "asset_status": 200,
        "asset_sha256": hashlib.sha256(asset_bytes).hexdigest(),
    }


def test_asset_repository_all_kinds_and_mpfb_tc_api_08(tmp_path, monkeypatch):
    """Test Case ID: TC-API-08. Register and query each artifact type and MPFB body."""
    url = f"sqlite+pysqlite:///{(tmp_path / 'repository.sqlite3').as_posix()}"
    engine = make_engine(url)
    Base.metadata.create_all(engine)
    sessions = make_session_factory(engine)
    bodies = BodyRepository(sessions)
    assets = AssetRepository(sessions)
    managed = tmp_path / "assets"
    managed.mkdir()
    settings = Settings(database_url=url, managed_asset_dir=managed)
    with TestClient(create_app(settings)) as client:
        storage = client.app.state.storage
        mesh = managed / "mpfb.glb"
        mesh.write_bytes(b"glTF" + b"0" * 100)
        registered = storage.register_mpfb_body("mpfb_test", mesh)
        assert bodies.get("mpfb_test").status == "ready"
        assert assets.get(registered.asset_id).body_id == "mpfb_test"
        assert client.get("/api/assets/body-mpfb_test.glb").status_code == 200
        for kind in ("original_image", "foreground_image", "mesh", "texture"):
            path = managed / f"{kind}.bin"
            path.write_bytes(kind.encode())
            row = storage.register_asset(path, kind=kind, media_type="application/octet-stream",
                                         body_id="mpfb_test")
            assert assets.get(row.asset_id).kind == kind
        assert len(assets.list(body_id="mpfb_test")) == 5
        assert len(assets.list(kind="texture")) == 1
        assert bodies.list(kind="mpfb", status="ready")[0].body_id == "mpfb_test"
        assert bodies.update_status("mpfb_test", "failed", error_code="TEST_FAILURE")
        assert bodies.get("mpfb_test").error_code == "TEST_FAILURE"
        assert assets.update_status(registered.asset_id, "missing")
        assert client.get("/api/assets/body-mpfb_test.glb").status_code == 404
    engine.dispose()


def test_asset_rejects_escape_and_missing_file_tc_api_02(tmp_path):
    """Test Case ID: TC-API-02. Unregistered, missing and out-of-root files are rejected."""
    url = f"sqlite+pysqlite:///{(tmp_path / 'negative.sqlite3').as_posix()}"
    engine = make_engine(url)
    Base.metadata.create_all(engine)
    managed = tmp_path / "assets"
    managed.mkdir()
    settings = Settings(database_url=url, managed_asset_dir=managed)
    with TestClient(create_app(settings)) as client:
        storage = client.app.state.storage
        outside = tmp_path / "outside.glb"
        outside.write_bytes(b"glTF")
        with pytest.raises(ValueError):
            storage.register_asset(outside, kind="glb", media_type="model/gltf-binary",
                                   public_name="outside.glb")
        missing = managed / "missing.glb"
        with pytest.raises(ValueError):
            storage.register_asset(missing, kind="glb", media_type="model/gltf-binary",
                                   public_name="missing.glb")
        assert client.get("/api/assets/outside.glb").status_code == 404
    engine.dispose()
