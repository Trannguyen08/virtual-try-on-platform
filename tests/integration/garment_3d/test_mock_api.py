from dataclasses import replace
from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from backend.garment3d.app import create_app
from backend.garment3d.settings import Garment3DSettings


def jpeg_bytes() -> bytes:
    output = BytesIO()
    Image.new("RGB", (512, 640), (50, 100, 180)).save(output, format="JPEG")
    return output.getvalue()


def test_mock_api_generates_downloadable_glb(tmp_path: Path) -> None:
    settings = replace(
        Garment3DSettings.from_environment(),
        provider="mock",
        output_dir=tmp_path / "outputs",
        sqlite_path=tmp_path / "jobs.sqlite3",
        poll_cache_seconds=0,
    )
    app = create_app(settings)

    with TestClient(app) as client:
        created = client.post(
            "/garment3d/generations",
            files={"front": ("front.jpg", jpeg_bytes(), "image/jpeg")},
        )
        assert created.status_code == 202, created.text
        payload = created.json()

        job = client.get(payload["poll_url"])
        assert job.status_code == 200
        assert job.json()["status"] == "completed"

        generation = client.get(job.json()["result_url"])
        assert generation.status_code == 200
        result = generation.json()
        assert result["mesh"]["triangle_count"] == 1
        assert "BACK_AND_SIDES_INFERRED_FROM_SINGLE_IMAGE" in result["warnings"]

        model = client.get(result["assets"]["glb_url"])
        assert model.status_code == 200
        assert model.content[:4] == b"glTF"


def test_queued_job_survives_application_restart(tmp_path: Path) -> None:
    settings = replace(
        Garment3DSettings.from_environment(),
        provider="mock",
        output_dir=tmp_path / "outputs",
        sqlite_path=tmp_path / "jobs.sqlite3",
        poll_cache_seconds=0,
    )
    with TestClient(create_app(settings)) as client:
        created = client.post(
            "/garment3d/generations",
            files={"front": ("front.jpg", jpeg_bytes(), "image/jpeg")},
        )
        assert created.status_code == 202
        poll_url = created.json()["poll_url"]

    with TestClient(create_app(settings)) as restarted_client:
        recovered = restarted_client.get(poll_url)
        assert recovered.status_code == 200
        assert recovered.json()["status"] == "completed"
