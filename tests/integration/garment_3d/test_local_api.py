import time
from dataclasses import replace
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from backend.garment3d.app import create_app
from backend.garment3d.settings import Garment3DSettings


def garment_png_bytes() -> bytes:
    image = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.polygon(
        [
            (170, 70),
            (60, 155),
            (105, 220),
            (145, 185),
            (145, 440),
            (367, 440),
            (367, 185),
            (407, 220),
            (452, 155),
            (342, 70),
            (310, 95),
            (202, 95),
        ],
        fill=(195, 55, 80, 255),
    )
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def test_local_api_generates_downloadable_body_ready_assets_tc_garment_int_01(
    tmp_path: Path,
) -> None:
    """TC-GARMENT-INT-01: local API returns input-derived GLB and fit metadata."""
    settings = replace(
        Garment3DSettings.from_environment(),
        provider="local",
        postprocessor="passthrough",
        output_dir=tmp_path / "outputs",
        sqlite_path=tmp_path / "jobs.sqlite3",
        poll_cache_seconds=0,
    )

    with TestClient(create_app(settings)) as client:
        created = client.post(
            "/garment3d/generations",
            files={"front": ("front.png", garment_png_bytes(), "image/png")},
            data={
                "garment_type": "tshirt",
                "reference_measurement": "garment_length",
                "reference_value_cm": "70",
            },
        )
        assert created.status_code == 202, created.text
        job = None
        for _ in range(100):
            response = client.get(created.json()["poll_url"])
            assert response.status_code == 200
            job = response.json()
            if job["status"] in {"completed", "failed"}:
                break
            time.sleep(0.02)

        assert job is not None
        assert job["status"] == "completed", job
        generation = client.get(job["result_url"]).json()
        assert generation["garment"]["fit_ready"] is True
        assert generation["garment"]["measurements"]["garment_length"][
            "value_cm"
        ] == pytest.approx(70.0, abs=0.1)

        glb = client.get(generation["assets"]["glb_url"])
        metadata = client.get(generation["assets"]["metadata_url"])
        assert glb.status_code == 200
        assert glb.content[:4] == b"glTF"
        assert metadata.status_code == 200
        assert metadata.json()["schema_version"] == "garment-fit-ready/1.0"
