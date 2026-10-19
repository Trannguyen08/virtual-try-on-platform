"""Contract and restart checks for calibrated image try-on jobs."""

from dataclasses import replace
from datetime import timedelta
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import update

from backend.core.config import Settings
from backend.db.models import Base, ImageTryOnRecord, utc_now
from backend.db.session import make_engine
from backend.garment3d.settings import Garment3DSettings
from backend.main import create_app
from backend.workers.image_tryon import ImageTryOnWorker, ProcessingError


def image_bytes() -> bytes:
    output = BytesIO()
    Image.new("RGB", (32, 32), (180, 40, 60)).save(output, format="PNG")
    return output.getvalue()


def setup_app(tmp_path: Path):
    url = f"sqlite+pysqlite:///{(tmp_path / 'jobs.sqlite3').as_posix()}"
    engine = make_engine(url)
    Base.metadata.create_all(engine)
    engine.dispose()
    managed = tmp_path / "assets"
    managed.mkdir()
    settings = Settings(database_url=url, managed_asset_dir=managed)
    garment_settings = replace(
        Garment3DSettings.from_environment(), provider="mock",
        output_dir=tmp_path / "garment", sqlite_path=tmp_path / "garment.sqlite3",
    )
    return settings, garment_settings


def register_body(client: TestClient, settings: Settings) -> str:
    body_id = "a" * 32
    body_path = settings.managed_asset_dir / "bodies" / f"{body_id}.glb"
    body_path.parent.mkdir(parents=True)
    fixture = Path(__file__).resolve().parents[3] / "backend" / "fixtures" / "assets" / "mock-body.glb"
    body_path.write_bytes(fixture.read_bytes())
    client.app.state.storage.register_mpfb_body(body_id, body_path, metadata={
        "mesh_unit": "m", "up_axis": "Y", "forward_axis": "+Z",
    })
    return body_id


def submit(client: TestClient, body_id: str, *, media_type: str = "image/png",
           content: bytes | None = None):
    return client.post(
        "/api/tryon/image-jobs",
        data={"body_id": body_id, "garment_type": "tshirt", "reference_value_cm": "70"},
        files={"front": ("shirt.png", image_bytes() if content is None else content, media_type)},
    )


def test_image_tryon_queue_survives_restart_tc_api_09(tmp_path: Path):
    """Test Case ID: TC-API-09. Upload and queue commit, then job survives API restart."""
    settings, garment_settings = setup_app(tmp_path)
    with TestClient(create_app(settings, garment3d_settings=garment_settings)) as first:
        body_id = register_body(first, settings)
        response = submit(first, body_id)
        assert response.status_code == 202, response.text
        created = response.json()["data"]
        assert created["status"] == "pending"
        assert created["request"]["reference_value_cm"] == pytest.approx(70.0)
        assert "views" not in created["request"]
        job_id = created["job_id"]
        assert first.get(f"/api/tryon/image-jobs/{job_id}").json()["data"]["status"] == "pending"
        assert first.get(f"/api/body-builder/bodies/{body_id}").status_code == 200
    with TestClient(create_app(settings, garment3d_settings=garment_settings)) as restarted:
        assert restarted.get(f"/api/tryon/image-jobs/{job_id}").json()["data"]["status"] == "pending"
        jobs = restarted.app.state.image_tryon.jobs
        claimed = jobs.claim()
        assert claimed is not None and claimed[0] == job_id
        assert jobs.finish(job_id, claimed[1], error={
            "code": "TEST_WORKER_FAILURE", "message": "Controlled failure", "details": [],
        })
        failed = restarted.get(f"/api/tryon/image-jobs/{job_id}").json()["data"]
        assert failed["status"] == "failed"
        assert failed["error"]["code"] == "TEST_WORKER_FAILURE"
        assert failed["result"] is None


def test_image_tryon_rejects_missing_body_and_bad_image_tc_api_02(tmp_path: Path):
    """Test Case ID: TC-API-02. Invalid body or bytes never create a queue entry."""
    settings, garment_settings = setup_app(tmp_path)
    with TestClient(create_app(settings, garment3d_settings=garment_settings)) as client:
        body_id = register_body(client, settings)
        assert submit(client, "missing").json()["error"]["code"] == "BODY_NOT_FOUND"
        assert submit(client, body_id, media_type="image/jpeg").json()["error"]["code"] == "INVALID_IMAGE"
        assert submit(client, body_id, media_type="image/bmp").status_code == 415
        assert submit(client, body_id, content=b"invalid").json()["error"]["code"] == "INVALID_IMAGE"
        assert client.app.state.image_tryon.jobs.claim() is None


def test_expired_tryon_lease_fails_after_two_attempts_tc_api_03(tmp_path: Path):
    """Test Case ID: TC-API-03. A crashed worker can retry, then times out safely."""
    settings, garment_settings = setup_app(tmp_path)
    with TestClient(create_app(settings, garment3d_settings=garment_settings)) as client:
        body_id = register_body(client, settings)
        job_id = submit(client, body_id).json()["data"]["job_id"]
        jobs = client.app.state.image_tryon.jobs
        first = jobs.claim()
        assert first is not None and first[1] == 1
        with jobs.sessions.begin() as session:
            session.execute(update(ImageTryOnRecord).where(
                ImageTryOnRecord.job_id == job_id,
            ).values(leased_until=utc_now() - timedelta(seconds=1)))
        second = jobs.claim()
        assert second is not None and second[1] == 2
        with jobs.sessions.begin() as session:
            session.execute(update(ImageTryOnRecord).where(
                ImageTryOnRecord.job_id == job_id,
            ).values(leased_until=utc_now() - timedelta(seconds=1)))
        assert jobs.claim() is None
        failed = jobs.get(job_id)
        assert failed is not None and failed.status == "failed"
        assert failed.error is not None and failed.error.code == "PROCESSING_TIMEOUT"


def test_worker_failure_is_structured_tc_api_03(tmp_path: Path, monkeypatch):
    """Test Case ID: TC-API-03. Provider failure becomes a failed job, not a crash."""
    settings, garment_settings = setup_app(tmp_path)
    with TestClient(create_app(settings, garment3d_settings=garment_settings)) as client:
        body_id = register_body(client, settings)
        job_id = submit(client, body_id).json()["data"]["job_id"]
        jobs = client.app.state.image_tryon.jobs
        worker = ImageTryOnWorker(settings, client.app.state.storage, jobs)

        def fail(_job_id, _request):
            raise ProcessingError("GARMENT_MASK_NOT_DETECTED", "No garment detected")

        monkeypatch.setattr(worker, "_process", fail)
        assert worker.run_once()
        failed = jobs.get(job_id)
        assert failed is not None and failed.status == "failed"
        assert failed.error is not None and failed.error.code == "GARMENT_MASK_NOT_DETECTED"
