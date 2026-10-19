"""TC-API-03: native artifact/provenance flow with mocked Blender only."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.core.errors import AppException
from backend.services import blender_body


@pytest.fixture
def native_jobs(tmp_path, monkeypatch):
    root = tmp_path / "assets"
    asset = root / "shirt"
    asset.mkdir(parents=True)
    (asset / "shirt.mhclo").write_text("obj_file shirt.obj\nverts 0\n0\n", encoding="utf-8")
    (asset / "shirt.obj").write_text("v 0 0 0\n", encoding="utf-8")
    entry = {"id": "test-refit", "name": "Refit", "category": "t_shirt", "sizes": ["M"],
             "assets": ["shirt"], "source": "fixture", "license": "CC0"}
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"version": 1, "garments": [entry]}), encoding="utf-8")
    monkeypatch.setenv("MPFB_ASSET_ROOT", str(root))
    monkeypatch.setenv("MPFB_GARMENT_CATALOG", str(catalog))
    monkeypatch.setattr(blender_body, "OUTPUT", tmp_path)
    monkeypatch.setattr(blender_body, "find_blender_executable", lambda: "blender")
    return blender_body.BlenderBodyJobs(), tmp_path


def fake_success(command, **kwargs):
    """Artifacts are fixtures, not valid Blender files or proof of real fitting."""
    output = Path(command[command.index("--output") + 1])
    action = command[command.index("--action") + 1]
    output.write_bytes(b"glTF" + b"\x00" * 128)
    if action == "body":
        output.with_suffix(".blend").write_bytes(b"BLENDER-fixture")
        marker = "BODY_METHOD=mpfb"
    else:
        output.with_suffix(".refit.json").write_text(json.dumps({
            "method": "blender_mpfb_refit", "garment_id": "test-refit",
            "mode": "body_refit", "cloth_simulation": False,
        }), encoding="utf-8")
        marker = "CLOTHING_METHOD=mpfb_refit"
    return SimpleNamespace(returncode=0, stdout=marker, stderr="")


def test_native_refit_method_requires_report_and_source_tc_api_03(native_jobs, monkeypatch):
    """Test Case ID: TC-API-03. Body→refit keeps native artifacts/provenance."""
    jobs, output = native_jobs
    monkeypatch.setattr(blender_body.subprocess, "run", fake_success)
    body = jobs.create("body", {})
    jobs.run(body["job_id"], {})
    assert jobs.get(body["job_id"])["status"] == "completed"
    params = {"garment_id": "test-refit", "category": "t_shirt", "size": "M"}
    clothing = jobs.create("clothing", params, body["job_id"])
    jobs.run(clothing["job_id"], params)
    result = jobs.get(clothing["job_id"])
    assert result["status"] == "completed"
    assert result["method"] == "blender_mpfb_refit"
    assert result["source"] == "module"
    assert (output / f"{body['job_id']}.blend").is_file()
    assert (output / f"{clothing['job_id']}.refit.json").is_file()


def test_legacy_body_requires_new_native_scene_tc_api_03(native_jobs):
    """Test Case ID: TC-API-03. Legacy GLB-only body cannot masquerade as refit."""
    jobs, _ = native_jobs
    body = jobs.create("body", {})
    jobs._jobs[body["job_id"]].update(status="completed", source="module")
    with pytest.raises(AppException) as error:
        jobs.create("clothing", {"garment_id": "test-refit", "category": "t_shirt", "size": "M"}, body["job_id"])
    assert error.value.error.code == "BODY_REFIT_DATA_MISSING"


def test_failed_native_export_does_not_complete_body_tc_api_03(native_jobs, monkeypatch):
    """Test Case ID: TC-API-03. GLB alone is insufficient for a new body job."""
    jobs, _ = native_jobs

    def missing_native(command, **kwargs):
        result = fake_success(command, **kwargs)
        output = Path(command[command.index("--output") + 1])
        output.with_suffix(".blend").unlink()
        return result

    monkeypatch.setattr(blender_body.subprocess, "run", missing_native)
    body = jobs.create("body", {})
    jobs.run(body["job_id"], {})
    assert jobs.get(body["job_id"])["status"] == "failed"


def test_refit_marker_without_report_fails_tc_api_03(native_jobs, monkeypatch):
    """Test Case ID: TC-API-03. A marker cannot claim an unaudited refit result."""
    jobs, _ = native_jobs
    monkeypatch.setattr(blender_body.subprocess, "run", fake_success)
    body = jobs.create("body", {})
    jobs.run(body["job_id"], {})

    def missing_report(command, **kwargs):
        result = fake_success(command, **kwargs)
        output = Path(command[command.index("--output") + 1])
        output.with_suffix(".refit.json").unlink()
        return result

    monkeypatch.setattr(blender_body.subprocess, "run", missing_report)
    params = {"garment_id": "test-refit", "category": "t_shirt", "size": "M"}
    clothing = jobs.create("clothing", params, body["job_id"])
    jobs.run(clothing["job_id"], params)
    assert jobs.get(clothing["job_id"])["status"] == "failed"


def test_catalog_route_reports_readiness_without_disk_paths_tc_api_03(native_jobs):
    """Test Case ID: TC-API-03. Operator status is additive and path-free."""
    from backend.api.body_builder import get_refit_garments

    response = get_refit_garments()
    assert response.data[0]["available"] is True
    assert response.data[0]["mode"] == "body_refit"
    assert str(native_jobs[1]) not in json.dumps(response.data)
