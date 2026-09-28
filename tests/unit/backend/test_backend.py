import json
import struct
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from pydantic import ValidationError

from backend.core.config import Settings
from backend.core.errors import AppException
from backend.main import create_app
from backend.schemas.body import BodySchema
from backend.schemas.common import ErrorResponse, SuccessResponse
from backend.schemas.fit import FitRequest
from backend.schemas.garment import GarmentSchema
from backend.schemas.job import JobSchema
from backend.services.assets import ASSET_NAMES, resolve_asset
from scripts.generate_mock_glb import BODY, SHIRT, build_glb


def assert_error(response, status, code):
    assert response.status_code == status
    error = ErrorResponse.model_validate(response.json())
    assert error.error.code == code
    return error.error


def test_health_catalog_and_docs(client):
    assert client.get("/health").json() == {"status": "healthy"}
    response = client.get("/api/garments")
    assert response.status_code == 200
    catalog = SuccessResponse[list[GarmentSchema]].model_validate(response.json()).data
    assert len(catalog) >= 1
    garment = catalog[0]
    assert garment.category == "t_shirt"
    assert [item.size for item in garment.sizes] == ["S", "M", "L", "XL"]
    assert garment.source == "mock"
    assert client.get("/docs").status_code == 200
    schema = client.get("/openapi.json").json()
    assert {"/health", "/api/garments", "/api/tryon/analyze", "/api/tryon/fit",
            "/api/jobs/{job_id}", "/api/assets/{asset_name}"} <= schema["paths"].keys()
    analyze = schema["paths"]["/api/tryon/analyze"]["post"]
    assert "multipart/form-data" in analyze["requestBody"]["content"]
    assert analyze["responses"]["422"]["content"]["application/json"]["schema"]["$ref"].endswith("ErrorResponse")


@pytest.mark.parametrize("image_format,mime,height", [("PNG", "image/png", 140), ("JPEG", "image/jpeg", 210)])
def test_analyze_valid_images(client, image_format, mime, height):
    buffer = BytesIO()
    Image.new("RGB", (16, 16), "blue").save(buffer, format=image_format)
    response = client.post("/api/tryon/analyze", data={"height_cm": str(height)},
                           files={"image": ("ignored-filename", buffer.getvalue(), mime)})
    assert response.status_code == 200
    body = SuccessResponse[BodySchema].model_validate(response.json()).data
    assert body.measurements.height_cm == height
    assert body.measurements.chest_cm == 96
    assert body.confidence is None and body.source == "mock"
    assert "fixed" in body.notes[0]


@pytest.mark.parametrize("height", ["139", "211", "NaN", "Infinity", "abc", ""])
def test_analyze_invalid_height(client, png_bytes, height):
    response = client.post("/api/tryon/analyze", data={"height_cm": height},
                           files={"image": ("test.png", png_bytes, "image/png")})
    assert_error(response, 422, "VALIDATION_ERROR")


def test_analyze_required_fields(client, png_bytes):
    assert_error(client.post("/api/tryon/analyze", data={"height_cm": "170"}), 422, "VALIDATION_ERROR")
    assert_error(client.post("/api/tryon/analyze", files={"image": ("test.png", png_bytes, "image/png")}),
                 422, "VALIDATION_ERROR")


@pytest.mark.parametrize("content,mime,status,code", [
    (b"", "image/png", 400, "INVALID_IMAGE"),
    (b"not an image", "image/png", 400, "INVALID_IMAGE"),
    (b"GIF89a", "image/gif", 415, "UNSUPPORTED_IMAGE_TYPE"),
    (b"x" * (5 * 1024 * 1024 + 1), "image/png", 413, "IMAGE_TOO_LARGE"),
], ids=["empty", "fake", "unsupported", "oversize"])
def test_analyze_bad_uploads(client, content, mime, status, code):
    response = client.post("/api/tryon/analyze", data={"height_cm": "170"},
                           files={"image": ("test.png", content, mime)})
    assert_error(response, status, code)


def test_analyze_mime_mismatch_truncated_and_pixel_limit(client, png_bytes):
    for content, mime in [(png_bytes, "image/jpeg"), (png_bytes[:30], "image/png")]:
        response = client.post("/api/tryon/analyze", data={"height_cm": "170"},
                               files={"image": ("test.png", content, mime)})
        assert_error(response, 400, "INVALID_IMAGE")
    with TestClient(create_app(Settings(max_image_pixels=32))) as small_client:
        response = small_client.post("/api/tryon/analyze", data={"height_cm": "170"},
                                     files={"image": ("test.png", png_bytes, "image/png")})
        assert_error(response, 413, "IMAGE_TOO_LARGE")


@pytest.mark.parametrize("size", ["S", "M", "L", "XL"])
def test_fit_all_sizes_and_job_identity(client, body, size):
    request = {"body_id": body["body_id"], "garment_id": "demo-tshirt", "size": size}
    response = client.post("/api/tryon/fit", json=request)
    assert response.status_code == 202
    created = SuccessResponse[JobSchema].model_validate(response.json()).data
    assert created.status == "pending" and created.result is None and created.error is None
    fetched = client.get(f"/api/jobs/{created.job_id}")
    assert fetched.status_code == 200
    job = SuccessResponse[JobSchema].model_validate(fetched.json()).data
    assert job.job_id == created.job_id and job.request.model_dump() == request
    assert job.status == "completed" and job.error is None
    assert job.result.body_id == body["body_id"] and job.result.size == size
    assert job.result.garment_id == "demo-tshirt"
    assert job.result.recommendation.size == "M"
    assert job.result.overall.label == {"S": "tight", "M": "good", "L": "loose", "XL": "loose"}[size]
    assert {region.region for region in job.result.regions} == {"chest", "waist", "hip", "shoulder"}
    for component in [job, job.result, job.result.overall, job.result.recommendation, *job.result.regions]:
        assert component.source == "mock"
    for component in [job.result.overall, *job.result.regions]:
        assert component.score is None and component.confidence is None
    assert job.result.recommendation.confidence is None


@pytest.mark.parametrize("change,status,code", [
    ({"body_id": "missing"}, 404, "BODY_NOT_FOUND"),
    ({"garment_id": "missing"}, 404, "GARMENT_NOT_FOUND"),
    ({"size": "XXL"}, 422, "VALIDATION_ERROR"),
    ({"size": "m"}, 422, "VALIDATION_ERROR"),
    ({"body_id": ""}, 422, "VALIDATION_ERROR"),
    ({"body_id": 123}, 422, "VALIDATION_ERROR"),
    ({"extra": True}, 422, "VALIDATION_ERROR"),
])
def test_fit_invalid_inputs(client, body, change, status, code):
    response = client.post("/api/tryon/fit", json={
        "body_id": body["body_id"], "garment_id": "demo-tshirt", "size": "M", **change,
    })
    assert_error(response, status, code)


def test_fit_missing_invalid_json_and_unknown_job(client):
    assert_error(client.post("/api/tryon/fit", json={}), 422, "VALIDATION_ERROR")
    assert_error(client.post("/api/tryon/fit", content=b"{bad", headers={"Content-Type": "application/json"}),
                 422, "VALIDATION_ERROR")
    assert_error(client.get("/api/jobs/job_missing"), 404, "JOB_NOT_FOUND")


def test_size_not_in_garment_catalog(app, client, body, monkeypatch):
    provider = app.state.orchestrator.provider
    catalog = provider.garments()
    catalog[0].sizes = catalog[0].sizes[:1]
    monkeypatch.setattr(provider, "garments", lambda: catalog)
    response = client.post("/api/tryon/fit", json={"body_id": body["body_id"], "garment_id": "demo-tshirt", "size": "XL"})
    assert_error(response, 422, "SIZE_NOT_AVAILABLE")


def test_failed_background_job_is_pollable_and_sanitized(app, client, body, monkeypatch):
    def fail(*args):
        raise RuntimeError("private internal path and exception")

    monkeypatch.setattr(app.state.orchestrator.provider, "fit", fail)
    created = client.post("/api/tryon/fit", json={"body_id": body["body_id"], "garment_id": "demo-tshirt", "size": "M"})
    assert created.status_code == 202
    response = client.get("/api/jobs/" + created.json()["data"]["job_id"])
    assert response.status_code == 200
    payload = SuccessResponse[JobSchema].model_validate(response.json())
    assert payload.error is None
    assert payload.data.status == "failed" and payload.data.result is None
    assert payload.data.error.code == "PROCESSING_FAILED"
    assert "private" not in response.text


def test_job_state_transitions_and_independent_stores(app, client, body):
    service = app.state.orchestrator
    request = FitRequest(body_id=body["body_id"], garment_id="demo-tshirt", size="M")
    job = service.jobs.create(request, "mock")
    assert client.get(f"/api/jobs/{job.job_id}").json()["data"]["status"] == "pending"

    def work():
        state = client.get(f"/api/jobs/{job.job_id}").json()["data"]
        assert state["status"] == "running"
        assert state["result"] is None and state["error"] is None
        return service.provider.fit(*service.fit_inputs(request), request)

    service.jobs.run(job.job_id, work)
    assert service.jobs.get(job.job_id).status == "completed"
    # A duplicate dispatch must not rerun a terminal job.
    service.jobs.run(job.job_id, lambda: pytest.fail("Duplicate execution"))
    with TestClient(create_app()) as restarted:
        assert_error(restarted.get(f"/api/jobs/{job.job_id}"), 404, "JOB_NOT_FOUND")
        assert_error(restarted.post("/api/tryon/fit", json=request.model_dump()), 404, "BODY_NOT_FOUND")


@pytest.mark.parametrize("state", ["pending", "running", "completed", "failed"])
def test_schema_rejects_impossible_job_state(state):
    invalid_error = None if state in ("completed", "failed") else {"code": "X", "message": "X"}
    with pytest.raises(ValidationError):
        JobSchema(job_id="job_test", status=state, source="mock", method="test", notes=[],
                  request=FitRequest(body_id="body_test", garment_id="demo-tshirt", size="M"),
                  result=None, error=invalid_error)


@pytest.mark.parametrize("name,boxes", [("mock-body.glb", BODY), ("mock-tshirt.glb", SHIRT), ("mock-tryon.glb", BODY + SHIRT)])
def test_assets_are_real_reproducible_glb(client, name, boxes):
    response = client.get("/api/assets/" + name)
    assert response.status_code == 200 and response.headers["content-type"] == "model/gltf-binary"
    content = response.content
    assert content == build_glb(boxes)
    magic, version, length = struct.unpack_from("<4sII", content)
    assert (magic, version, length) == (b"glTF", 2, len(content))
    json_length, chunk_type = struct.unpack_from("<I4s", content, 12)
    assert chunk_type == b"JSON" and json_length % 4 == 0
    document = json.loads(content[20:20 + json_length])
    assert document["asset"]["version"] == "2.0" and document["extras"]["source"] == "mock"
    bin_length, bin_type = struct.unpack_from("<I4s", content, 20 + json_length)
    assert bin_type == b"BIN\0" and bin_length == document["buffers"][0]["byteLength"]
    assert 28 + json_length + bin_length == len(content)
    binary = content[28 + json_length:]
    for view in document["bufferViews"]:
        assert view["byteOffset"] + view["byteLength"] <= len(binary)
    assert max(struct.unpack_from("<36H", binary, 96)) < document["accessors"][0]["count"]


@pytest.mark.parametrize("path", [
    "%2e%2e/requirements.txt", "%2e%2e%5cmain.py", "%252e%252e%252fmain.py",
    "C:%5cWindows%5cwin.ini", "%2fetc%2fpasswd", "mock-body.glb/../../main.py",
    "unknown.glb", "catalog.json", "mock-body.glb%00",
])
def test_asset_traversal_and_unregistered_files(client, path):
    response = client.get("/api/assets/" + path)
    assert response.status_code == 404
    ErrorResponse.model_validate(response.json())


def test_asset_resolved_path_cannot_escape_root(tmp_path, monkeypatch):
    # Deterministic simulation of a symlink/junction; Windows need not allow symlink creation.
    outside = tmp_path.parent / "outside.glb"
    from pathlib import Path
    original = Path.resolve

    def resolve(path, *args, **kwargs):
        return outside if path.name in ASSET_NAMES else original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolve)
    with pytest.raises(AppException) as error:
        resolve_asset(tmp_path, "mock-body.glb")
    assert error.value.status_code == 404


def test_missing_assets_are_null(tmp_path, png_bytes):
    with TestClient(create_app(Settings(asset_dir=tmp_path))) as client:
        assert client.get("/api/garments").json()["data"][0]["mesh"] is None
        body = client.post("/api/tryon/analyze", data={"height_cm": "170"},
                           files={"image": ("demo.png", png_bytes, "image/png")}).json()["data"]
        assert body["mesh"] is None
        created = client.post("/api/tryon/fit", json={"body_id": body["body_id"], "garment_id": "demo-tshirt", "size": "M"})
        result = client.get("/api/jobs/" + created.json()["data"]["job_id"]).json()["data"]["result"]
        assert all(asset is None for asset in result["assets"].values())
        assert_error(client.get("/api/assets/mock-body.glb"), 404, "ASSET_NOT_FOUND")


def test_cors_allows_only_configured_origins(client):
    for origin, status in [("http://localhost:5173", 200), ("https://untrusted.example", 400)]:
        response = client.options("/api/tryon/fit", headers={
            "Origin": origin, "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        })
        assert response.status_code == status
        assert response.headers.get("access-control-allow-origin") == (origin if status == 200 else None)
    with pytest.raises(ValueError):
        Settings(cors_origins=("*",))


def test_unexpected_api_error_uses_safe_envelope(app, monkeypatch):
    def fail():
        raise RuntimeError("private catalog path")

    monkeypatch.setattr(app.state.orchestrator.provider, "garments", fail)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/api/garments")
    assert_error(response, 500, "INTERNAL_ERROR")
    assert "private" not in response.text
