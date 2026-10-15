import json
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from garment.reconstruction.contracts import (
    GarmentImage,
    GarmentView,
    GenerationOptions,
    GenerationRequest,
)
from garment.reconstruction.errors import ReconstructionError
from garment.reconstruction.local_pipeline import LocalGarmentReconstructor
from garment.reconstruction.validation import GlbValidator


def garment_png(path: Path) -> Path:
    image = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.polygon(
        [
            (170, 70),
            (115, 105),
            (55, 160),
            (105, 220),
            (145, 185),
            (145, 440),
            (367, 440),
            (367, 185),
            (407, 220),
            (457, 160),
            (397, 105),
            (342, 70),
            (310, 95),
            (202, 95),
        ],
        fill=(35, 105, 190, 255),
    )
    image.save(path)
    return path


def request_for(path: Path, *, calibrated: bool = True) -> GenerationRequest:
    return GenerationRequest(
        images=(
            GarmentImage(
                view=GarmentView.FRONT,
                path=path,
                sha256="fixture",
                media_type="image/png",
                width=512,
                height=512,
            ),
        ),
        options=GenerationOptions(
            garment_type="tshirt",
            reference_measurement="garment_length" if calibrated else None,
            reference_value_cm=70.0 if calibrated else None,
        ),
    )


def test_local_pipeline_generates_fit_ready_textured_glb_tc_garment_01(
    tmp_path: Path,
) -> None:
    """TC-GARMENT-01: calibrated input produces GLB and body-ready metadata."""
    source = garment_png(tmp_path / "shirt.png")

    result = LocalGarmentReconstructor(grid_resolution=32).reconstruct(
        request_for(source), tmp_path / "output"
    )

    mesh = GlbValidator().validate(result.model_path)
    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert mesh.triangle_count and mesh.triangle_count > 100
    assert mesh.texture_count >= 1
    assert metadata["fit_ready"] is True
    assert metadata["coordinate_system"]["up_axis"] == "Y"
    assert metadata["measurements"]["garment_length"]["value_cm"] == pytest.approx(
        70.0, abs=0.1
    )
    assert {"shoulders", "chest", "waist"}.issubset(
        metadata["attachment_regions"]
    )
    assert "neck" in metadata["openings"]


def test_local_pipeline_marks_uncalibrated_output_not_fit_ready_tc_garment_02(
    tmp_path: Path,
) -> None:
    """TC-GARMENT-02: missing real-world scale never claims fit readiness."""
    result = LocalGarmentReconstructor(grid_resolution=28).reconstruct(
        request_for(garment_png(tmp_path / "shirt.png"), calibrated=False),
        tmp_path / "output",
    )

    assert result.metadata["fit_ready"] is False
    assert result.metadata["measurements"]["shoulder_width"]["value_cm"] is None
    assert "ABSOLUTE_SCALE_NOT_CALIBRATED" in result.metadata["warnings"]


def test_local_pipeline_rejects_image_without_garment_tc_garment_03(
    tmp_path: Path,
) -> None:
    """TC-GARMENT-03: a uniform image fails instead of returning a fake model."""
    source = tmp_path / "empty.png"
    Image.new("RGB", (512, 512), (255, 255, 255)).save(source)

    with pytest.raises(ReconstructionError) as error:
        LocalGarmentReconstructor(grid_resolution=28).reconstruct(
            request_for(source), tmp_path / "output"
        )

    assert error.value.code == "GARMENT_MASK_NOT_DETECTED"
