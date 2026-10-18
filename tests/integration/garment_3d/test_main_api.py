from dataclasses import replace
from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from backend.garment3d.settings import Garment3DSettings
from backend.main import create_app


def test_garment_generation_on_main_api_tc_garment_int_02(tmp_path: Path) -> None:
    """TC-GARMENT-INT-02: main API serves garment jobs and GLB on one origin."""
    settings = replace(
        Garment3DSettings.from_environment(),
        provider="mock",
        output_dir=tmp_path / "outputs",
        sqlite_path=tmp_path / "jobs.sqlite3",
        poll_cache_seconds=0,
    )
    image = BytesIO()
    Image.new("RGB", (512, 640), (50, 100, 180)).save(image, format="JPEG")

    with TestClient(create_app(garment3d_settings=settings)) as client:
        assert client.get("/health").status_code == 200
        garment_health = client.get("/garment3d/health")
        assert garment_health.status_code == 200
        assert garment_health.json()["provider"] == "mock"
        created = client.post(
            "/garment3d/generations",
            files={"front": ("front.jpg", image.getvalue(), "image/jpeg")},
            headers={"Origin": "http://localhost:5173"},
        )
        assert created.status_code == 202, created.text
        assert created.headers["access-control-allow-origin"] == "http://localhost:5173"

        job = client.get(created.json()["poll_url"])
        assert job.status_code == 200
        assert job.json()["status"] == "completed"

        generation = client.get(job.json()["result_url"])
        assert generation.status_code == 200
        model = client.get(generation.json()["assets"]["glb_url"])
        assert model.status_code == 200
        assert model.content[:4] == b"glTF"
