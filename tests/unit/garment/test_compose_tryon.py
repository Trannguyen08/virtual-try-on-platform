"""Fast geometry checks for static garment placement in Blender."""

import pytest

from garment.simulation.blender.compose_tryon import (
    torso_depth_center,
    validate_surface_adjustment,
)


def _body_points(fractions: tuple[float, ...]) -> list[tuple[float, float, float]]:
    points = []
    for fraction in fractions:
        height = fraction * 1.8
        for x in (-0.08, -0.04, 0.0, 0.04, 0.08):
            points.extend(((x, -0.12, height), (x, 0.08, height)))
    # A protruding head skews the whole-body bounding box toward the front.
    points.extend(((0.0, 0.65, 1.7), (0.0, -0.12, 1.7)))
    return points


def test_top_placement_uses_torso_depth_tc_gar_05() -> None:
    """TC-GAR-05: head protrusion must not move a top away from the torso."""
    points = _body_points((0.60, 0.68, 0.74))

    center = torso_depth_center(
        points, center_x=0.0, bottom_z=0.0,
        body_height=1.8, category="tshirt",
    )

    assert center == pytest.approx(-0.02, abs=1e-6)


def test_pants_placement_uses_pelvis_depth_tc_gar_05() -> None:
    """TC-GAR-05: trousers must center on the pelvis, not the head bounds."""
    points = _body_points((0.51, 0.56, 0.61))

    center = torso_depth_center(
        points, center_x=0.0, bottom_z=0.0,
        body_height=1.8, category="pants",
    )

    assert center == pytest.approx(-0.02, abs=1e-6)


def test_missing_torso_reports_error_tc_gar_05() -> None:
    """TC-GAR-05: an invalid body cannot silently use whole-body bounds."""
    with pytest.raises(ValueError, match="BODY_TORSO_MISSING"):
        torso_depth_center(
            [(0.0, 0.0, 1.7)], center_x=0.0, bottom_z=0.0,
            body_height=1.8, category="pants",
        )


def test_undersized_pants_are_rejected_tc_gar_05() -> None:
    """TC-GAR-05: excessive warping cannot pass as a fitted garment."""
    with pytest.raises(ValueError, match="SEVERE_MESH_PENETRATION"):
        validate_surface_adjustment(29298, 54016)


def test_compatible_pants_pass_adjustment_check_tc_gar_05() -> None:
    """TC-GAR-05: modest clearance corrections remain valid."""
    validate_surface_adjustment(4209, 54016)
