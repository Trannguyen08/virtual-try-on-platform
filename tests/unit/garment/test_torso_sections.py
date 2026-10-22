"""Analytic triangle-cut regressions, independent of Blender."""

import math

import pytest

from garment.mesh.torso_sections import TorsoSections
from garment.mesh.tshirt_geometry import build_tshirt


def add_box(vertices, triangles, x0, x1, y0, y1):
    offset = len(vertices)
    vertices.extend([(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0),
                     (x0, y0, 1.7), (x1, y0, 1.7), (x1, y1, 1.7), (x0, y1, 1.7)])
    for quad in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                 (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        a, b, c, d = (offset + i for i in quad)
        triangles.extend([(a, b, c), (a, c, d)])


def sections_with_offset_torso_and_arms():
    vertices, triangles = [], []
    add_box(vertices, triangles, -0.22, 0.22, 1, 1.26)
    add_box(vertices, triangles, -0.5, -0.4, 1, 1.1)
    add_box(vertices, triangles, 0.4, 0.5, 1, 1.1)
    return TorsoSections(vertices, triangles, 1.7)


def test_section_uses_actual_center_and_excludes_separate_arms_tc_gar_02():
    """Test Case ID: TC-GAR-02.

    Target: Triangle cuts with an offset torso, separate arms and no vertices
    in the waist band. Expected: Correct torso center and finite radial profile
    in all directions, independent of a guessed interior origin.
    """
    sections = sections_with_offset_torso_and_arms()
    z = 0.57 * 1.7
    assert sections.center(z) == pytest.approx((0, 1.13))
    assert sections.radius(z, 0) == pytest.approx(0.22)
    assert sections.radius(z, math.pi / 2) == pytest.approx(0.13)
    for i in range(32):
        radius = sections.radius(z, i * 2 * math.pi / 32)
        assert radius is not None and math.isfinite(radius) and radius > 0


def test_tshirt_follows_offset_section_centers_tc_gar_02():
    """Test Case ID: TC-GAR-02.

    Target: Integration of triangle sections into T-shirt geometry.
    Expected: Shirt sits around the measured offset torso, not the origin.
    """
    sections = sections_with_offset_torso_and_arms()
    center = sections.center(0.53 * 1.7)
    vertices, faces = build_tshirt(1.7, 0, center, sections.radius,
                                   {-1: (-1, -0.4), 1: (1, -0.4)},
                                   sample_center=sections.center)
    assert faces
    assert vertices[0] == pytest.approx((0.245, 1.13, 0.46 * 1.7))
    assert vertices[8] == pytest.approx((0, 1.285, 0.46 * 1.7))


def test_missing_triangle_cut_remains_explicit_tc_gar_02():
    """Test Case ID: TC-GAR-02.

    Target: A plane outside the body mesh.
    Expected: No fabricated profile, clear error when its center is requested.
    """
    sections = sections_with_offset_torso_and_arms()
    assert sections.radius(3, 0) is None
    with pytest.raises(ValueError, match="No central torso section"):
        sections.center(3)


def test_shoulder_surface_ignores_head_and_lower_body_tc_gar_02():
    """Test Case ID: TC-GAR-02.

    Target: Vertical shoulder sampling on a sloped analytic triangle.
    Expected: Correct shoulder height, excluding surfaces outside the band.
    """
    vertices = [(-1, -1, 1.3), (1, -1, 1.5), (0, 1, 1.4),
                (-1, -1, 1.1), (1, -1, 1.1), (0, 1, 1.1),
                (-1, -1, 1.65), (1, -1, 1.65), (0, 1, 1.65)]
    sections = TorsoSections(vertices, [(0, 1, 2), (3, 4, 5), (6, 7, 8)], 1.7)
    assert sections.surface_height(0, 0, 1.2, 1.55) == pytest.approx(1.4)
    assert sections.surface_height(0.25, 0, 1.2, 1.55) == pytest.approx(1.425)
    assert sections.surface_height(2, 0, 1.2, 1.55) is None
