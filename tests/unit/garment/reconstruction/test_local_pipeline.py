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


def soccer_kit_png(path: Path, touching: bool = False) -> Path:
    """Create a synthetic football kit: prominent jersey + smaller folded shorts below."""
    image = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # 1. Prominent football jersey (top)
    jersey_polygon = [
        (170, 40),
        (115, 75),
        (55, 130),
        (105, 190),
        (145, 155),
        (145, 340),
        (367, 340),
        (367, 155),
        (407, 190),
        (457, 130),
        (397, 75),
        (342, 40),
        (310, 65),
        (202, 65),
    ]
    draw.polygon(jersey_polygon, fill=(220, 20, 60, 255))  # Crimson jersey

    # 2. Folded shorts (smaller block below the jersey)
    shorts_top = 340 if touching else 365
    draw.rectangle([180, shorts_top, 332, shorts_top + 100], fill=(25, 25, 112, 255))  # Navy folded shorts

    image.save(path)
    return path


def test_local_pipeline_isolates_salient_jersey_from_soccer_kit_tc_garment_04(
    tmp_path: Path,
) -> None:
    """TC-GARMENT-04: multi-entity image (jersey + folded shorts) isolates the jersey."""
    source = soccer_kit_png(tmp_path / "soccer_kit.png", touching=False)
    result = LocalGarmentReconstructor(grid_resolution=32).reconstruct(
        request_for(source), tmp_path / "output"
    )

    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert metadata["segmentation"]["multi_entity_detected"] is True
    assert metadata["segmentation"]["salient_garment_isolated"] is True
    assert metadata["segmentation"]["discarded_entities_count"] >= 1
    assert "MULTI_ENTITY_SALIENT_GARMENT_ISOLATED" in metadata["warnings"]

    # Check that bottom landmark corresponds to jersey hem (~340px), not folded shorts bottom (~465px)
    garment_bottom_y = metadata["landmarks"]["garment_bottom"][1]
    assert garment_bottom_y < 360.0


def test_local_pipeline_isolates_touching_folded_shorts_tc_garment_05(
    tmp_path: Path,
) -> None:
    """TC-GARMENT-05: touching jersey + folded shorts are decoupled and jersey is isolated."""
    source = soccer_kit_png(tmp_path / "touching_kit.png", touching=True)
    result = LocalGarmentReconstructor(grid_resolution=32).reconstruct(
        request_for(source), tmp_path / "output"
    )

    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert metadata["segmentation"]["multi_entity_detected"] is True
    assert "MULTI_ENTITY_SALIENT_GARMENT_ISOLATED" in metadata["warnings"]
    garment_bottom_y = metadata["landmarks"]["garment_bottom"][1]
    assert garment_bottom_y < 360.0


def test_local_pipeline_preserves_sleeve_and_chest_details_tc_garment_06(
    tmp_path: Path,
) -> None:
    """TC-GARMENT-06: high-contrast sleeve stripes and chest crests are preserved."""
    image = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    jersey_polygon = [
        (170, 70), (115, 105), (55, 160), (105, 220), (145, 185),
        (145, 440), (367, 440), (367, 185), (407, 220), (457, 160),
        (397, 105), (342, 70), (310, 95), (202, 95),
    ]
    draw.polygon(jersey_polygon, fill=(20, 20, 20, 255))
    # Bright white sleeve stripes
    draw.line([(55, 160), (115, 105)], fill=(255, 255, 255, 255), width=8)
    draw.line([(457, 160), (397, 105)], fill=(255, 255, 255, 255), width=8)
    # Golden crest on outer left chest
    draw.ellipse([160, 200, 195, 235], fill=(255, 215, 0, 255))
    source = tmp_path / "striped_jersey.png"
    image.save(source)

    result = LocalGarmentReconstructor(grid_resolution=32).reconstruct(
        request_for(source), tmp_path / "output"
    )
    mesh = GlbValidator().validate(result.model_path)
    assert mesh.has_pbr_material is True
    assert mesh.texture_count >= 1


def test_local_pipeline_isolates_white_jersey_on_carpet_with_banner_tc_garment_07(
    tmp_path: Path,
) -> None:
    """TC-GARMENT-07: Real RGB soccer kit on gray carpet with bottom blue banner isolates white jersey, not folded shorts."""
    # Create non-transparent RGB image
    image = Image.new("RGB", (512, 512), (135, 135, 135))  # Gray carpet background
    draw = ImageDraw.Draw(image)

    # 1. White football jersey (spread prominently in upper portion)
    jersey_polygon = [
        (170, 40),
        (115, 75),
        (55, 130),
        (105, 190),
        (145, 155),
        (145, 340),
        (367, 340),
        (367, 155),
        (407, 190),
        (457, 130),
        (397, 75),
        (342, 40),
        (310, 65),
        (202, 65),
    ]
    draw.polygon(jersey_polygon, fill=(245, 245, 245))
    draw.ellipse([220, 120, 290, 190], fill=(0, 140, 60))

    # 2. Folded black shorts at bottom-left corner
    draw.rectangle([60, 360, 190, 465], fill=(15, 15, 15))

    # 3. Bottom advertising banner across bottom border (ZALO / shop hotline)
    draw.rectangle([0, 475, 512, 512], fill=(0, 85, 160))

    source = tmp_path / "soccer_kit_with_banner.jpg"
    image.save(source, "JPEG")

    result = LocalGarmentReconstructor(grid_resolution=32).reconstruct(
        request_for(source), tmp_path / "output"
    )

    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert metadata["segmentation"]["salient_garment_isolated"] is True
    assert metadata["segmentation"]["discarded_entities_count"] >= 1

    # Check that bottom landmark points to the white jersey hem (~340px), NOT the bottom of folded shorts (~465px)
    garment_bottom_y = metadata["landmarks"]["garment_bottom"][1]
    assert garment_bottom_y < 365.0

    mesh = GlbValidator().validate(result.model_path)
    assert mesh.triangle_count and mesh.triangle_count > 100


def test_local_pipeline_auto_detects_tshirt_and_preserves_sleeves_tc_garment_08(
    tmp_path: Path,
) -> None:
    """TC-GARMENT-08: garment_type='auto' automatically identifies tshirt and preserves both sleeves."""
    source = garment_png(tmp_path / "shirt.png")
    request = GenerationRequest(
        images=(
            GarmentImage(
                view=GarmentView.FRONT,
                path=source,
                sha256="fixture",
                media_type="image/png",
                width=512,
                height=512,
            ),
        ),
        options=GenerationOptions(
            garment_type="auto",
        ),
    )

    result = LocalGarmentReconstructor(grid_resolution=32).reconstruct(
        request, tmp_path / "output"
    )

    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert metadata["garment_type"] == "tshirt"
    assert metadata["auto_detected"] is True
    assert "GARMENT_TYPE_AUTO_DETECTED" in metadata["warnings"]

    # Verify both sleeves are preserved and not amputated by distance transform
    left_sleeve_x = metadata["landmarks"]["left_sleeve_end"][0]
    right_sleeve_x = metadata["landmarks"]["right_sleeve_end"][0]
    assert left_sleeve_x < 110.0  # Left sleeve extends to far left
    assert right_sleeve_x > 400.0  # Right sleeve extends to far right


def test_local_pipeline_auto_detects_pants_tc_garment_09(
    tmp_path: Path,
) -> None:
    """TC-GARMENT-09: garment_type='auto' identifies pants from split two-leg silhouette."""
    image = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # Draw trousers: waistband at top, splitting into two legs below y=240
    pants_polygon = [
        (180, 50),
        (332, 50),
        (345, 230),
        (355, 470),
        (280, 470),
        (265, 250),  # crotch center
        (250, 250),
        (235, 470),
        (160, 470),
        (170, 230),
    ]
    draw.polygon(pants_polygon, fill=(40, 50, 70, 255))
    source = tmp_path / "pants.png"
    image.save(source)

    request = GenerationRequest(
        images=(
            GarmentImage(
                view=GarmentView.FRONT,
                path=source,
                sha256="fixture",
                media_type="image/png",
                width=512,
                height=512,
            ),
        ),
        options=GenerationOptions(
            garment_type="auto",
        ),
    )

    result = LocalGarmentReconstructor(grid_resolution=32).reconstruct(
        request, tmp_path / "output"
    )

    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert metadata["garment_type"] == "pants"
    assert metadata["auto_detected"] is True


def test_local_pipeline_hollow_hem_opening_tc_garment_10(
    tmp_path: Path,
) -> None:
    """TC-GARMENT-10: bottom hem of top garment is a hollow unbridged opening."""
    source = garment_png(tmp_path / "shirt.png")
    result = LocalGarmentReconstructor(grid_resolution=32).reconstruct(
        request_for(source), tmp_path / "output"
    )

    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert "hem" in metadata["openings"]
    assert len(metadata["openings"]["hem"]["vertex_indices"]) > 0


def test_local_pipeline_occluded_shirt_reconstructs_valid_mesh_tc_garment_11(
    tmp_path: Path,
) -> None:
    """TC-GARMENT-11: occluded shirt reconstructs valid 3D shell without crash."""
    image = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # Draw shirt with cut bite on lower-left flank
    cut_shirt_polygon = [
        (170, 70), (115, 105), (55, 160), (105, 220), (145, 185),
        (145, 300),
        (220, 300),  # bite/occlusion from left
        (220, 440),
        (367, 440), (367, 185), (407, 220), (457, 160),
        (397, 105), (342, 70), (310, 95), (202, 95),
    ]
    draw.polygon(cut_shirt_polygon, fill=(240, 240, 240, 255))
    source = tmp_path / "occluded_shirt.png"
    image.save(source)

    result = LocalGarmentReconstructor(grid_resolution=32).reconstruct(
        request_for(source), tmp_path / "output"
    )

    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert metadata["segmentation"]["coverage_ratio"] > 0.05
    mesh = GlbValidator().validate(result.model_path)
    assert mesh.triangle_count and mesh.triangle_count > 100


def test_local_pipeline_tilted_shirt_reconstructs_valid_mesh_tc_garment_12(
    tmp_path: Path,
) -> None:
    """TC-GARMENT-12: tilted shirt reconstructs valid 3D shell without crash."""
    image = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    shirt_poly = [
        (170, 70), (115, 105), (55, 160), (105, 220), (145, 185),
        (145, 440), (367, 440), (367, 185), (407, 220), (457, 160),
        (397, 105), (342, 70), (310, 95), (202, 95),
    ]
    draw.polygon(shirt_poly, fill=(240, 240, 240, 255))
    # Cut bite on lower-left flank
    draw.rectangle([130, 310, 230, 450], fill=(0, 0, 0, 0))

    # Rotate 10 degrees to simulate tilted laying
    tilted = image.rotate(10, resample=Image.BICUBIC, center=(256, 256))
    source = tmp_path / "tilted_shirt.png"
    tilted.save(source)

    result = LocalGarmentReconstructor(grid_resolution=32).reconstruct(
        request_for(source), tmp_path / "output"
    )

    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert metadata["segmentation"]["coverage_ratio"] > 0.05
    mesh = GlbValidator().validate(result.model_path)
    assert mesh.triangle_count and mesh.triangle_count > 100


def test_local_pipeline_blank_back_texture_tc_garment_13(
    tmp_path: Path,
) -> None:
    """TC-GARMENT-13: back of garment is a blank surface carrying dominant front color."""
    source = garment_png(tmp_path / "shirt.png")
    result = LocalGarmentReconstructor(grid_resolution=32).reconstruct(
        request_for(source), tmp_path / "output"
    )

    scene = trimesh.load(result.model_path, force="scene")
    back_geom = scene.geometry.get("GarmentBack")
    assert back_geom is not None
    # Verify back texture exists and has uniform dominant base color
    back_tex = back_geom.visual.material.baseColorTexture
    assert back_tex is not None
    tex_arr = np.asarray(back_tex)
    # Check that back texture has zero variance / uniform plain color
    assert np.std(tex_arr[..., 0]) < 1.0





