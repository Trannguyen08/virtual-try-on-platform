"""Topology and sizing checks independent of Blender or model downloads."""

from collections import Counter, defaultdict
import math

import pytest

from garment.mesh.tshirt_geometry import build_tshirt


def torso_radius(z, angle):
    return 1 / math.sqrt((math.cos(angle) / 0.22) ** 2
                         + (math.sin(angle) / 0.13) ** 2)


def make_shirt(size="M", sampler=torso_radius):
    return build_tshirt(1.7, 0, (0, 0), sampler,
                        {-1: (-1, -0.4), 1: (1, -0.4)}, size)


def test_connected_surface_with_four_openings_tc_gar_02():
    """Test Case ID: TC-GAR-02.

    Target: Synthetic T-shirt surface topology before thickness/export.
    Expected: One connected surface, four boundary loops, no non-manifold
    edges, finite coordinates and fewer than 30,000 vertices.
    """
    vertices, faces = make_shirt()
    assert 0 < len(vertices) <= 30000
    assert all(math.isfinite(value) for vertex in vertices for value in vertex)
    edges = Counter()
    neighbours = defaultdict(set)
    for face in faces:
        assert len(set(face)) == 4
        for first, second in zip(face, face[1:] + face[:1]):
            edges[tuple(sorted((first, second)))] += 1
            neighbours[first].add(second)
            neighbours[second].add(first)
    assert set(edges.values()) == {1, 2}

    def component(seed, graph):
        seen, pending = set(), [seed]
        while pending:
            current = pending.pop()
            if current not in seen:
                seen.add(current)
                pending.extend(graph[current] - seen)
        return seen

    assert len(component(0, neighbours)) == len(vertices)
    boundary = defaultdict(set)
    for (first, second), uses in edges.items():
        if uses == 1:
            boundary[first].add(second)
            boundary[second].add(first)
    assert all(len(adjacent) == 2 for adjacent in boundary.values())
    remaining, loops = set(boundary), 0
    while remaining:
        remaining -= component(next(iter(remaining)), boundary)
        loops += 1
    assert loops == 4


def test_synthetic_ease_increases_by_size_tc_gar_02():
    """Test Case ID: TC-GAR-02.

    Target: Metre-scale synthetic template ease, not size-chart compliance.
    Expected: Size changes torso clearance while the neckline stays fixed.
    """
    small, _ = make_shirt("S")
    medium, _ = make_shirt("M")
    large, _ = make_shirt("L")
    assert small[0][0] == pytest.approx(0.238)
    assert medium[0][0] == pytest.approx(0.245)
    assert large[0][0] == pytest.approx(0.255)
    assert small[0][2] == pytest.approx(large[0][2])
    # Compare the back neckline, whose height is fixed across sizes.
    small_neck = [p for p in small if abs(p[2] - 1.7 * 0.85) < 1e-9]
    large_neck = [p for p in large if abs(p[2] - 1.7 * 0.85) < 1e-9]
    assert small_neck
    assert len(small_neck) == len(large_neck)
    for first, second in zip(small_neck, large_neck):
        assert first == pytest.approx(second)


@pytest.mark.parametrize("radius", [None, 0, -0.1, float("nan")])
def test_missing_torso_fails_explicitly_tc_gar_02(radius):
    """Test Case ID: TC-GAR-02.

    Target: Invalid body sampling fallback.
    Expected: A clear error instead of exporting misleading geometry.
    """
    with pytest.raises(ValueError, match="continuous torso"):
        make_shirt(sampler=lambda z, angle: radius)


@pytest.mark.parametrize("first_complete_level", [0.53, 0.57, 0.61])
def test_hem_bridges_leg_gap_from_measured_hip_tc_gar_02(first_complete_level):
    """Test Case ID: TC-GAR-02.

    Target: Body with no closed cross-section at the hanging shirt hem.
    Expected: Complete shirt; hem uses the measured hip profile and retains
    its intended height, rather than requiring a body surface between legs.
    """
    def pelvis_sampler(z, angle):
        if z < first_complete_level * 1.7 - 1e-9:
            return None
        return torso_radius(z, angle) + (z / 1.7 - first_complete_level) * 0.02

    vertices, faces = make_shirt(sampler=pelvis_sampler)
    assert faces
    assert vertices[0][0] == pytest.approx(0.245)
    assert vertices[0][2] == pytest.approx(0.46 * 1.7)
    for j in range(32):
        x, y, z = vertices[j]
        angle = 2 * math.pi * j / 32
        expected = torso_radius(first_complete_level * 1.7, angle) + 0.025
        assert math.hypot(x, y) == pytest.approx(expected)
        assert z == pytest.approx(0.46 * 1.7)


def test_missing_upper_torso_is_not_hidden_by_hem_extension_tc_gar_02():
    """Test Case ID: TC-GAR-02.

    Target: Missing chest surface above a valid hip anchor.
    Expected: Explicit error identifying the failed chest sampling level.
    """
    def missing_chest(z, angle):
        if abs(z / 1.7 - 0.65) < 1e-9:
            return None
        return torso_radius(z, angle)

    with pytest.raises(ValueError, match="height ratio=0.65"):
        make_shirt(sampler=missing_chest)


def test_shoulder_clearance_keeps_hem_and_collar_fixed_tc_gar_02():
    """Test Case ID: TC-GAR-02.

    Target: Body shoulder above the original proportional shirt shoulder.
    Expected: Shoulder lifted 6 mm over body; hem and collar retained.
    """
    original, original_faces = make_shirt()
    fitted, fitted_faces = build_tshirt(
        1.7, 0, (0, 0), torso_radius, {-1: (-1, -0.4), 1: (1, -0.4)},
        sample_shoulder_height=lambda x, y: 1.42,
    )
    assert fitted_faces == original_faces
    for first, second in zip(original[:32], fitted[:32]):
        assert first == pytest.approx(second)
    shoulder = [i for i, p in enumerate(original)
                if abs(p[0] - (0.145 * 1.7 + 0.025)) < 1e-9
                and abs(p[1]) < 1e-9
                and abs(p[2] - 1.7 * (0.815 - 0.018)) < 1e-9]
    assert shoulder
    assert fitted[shoulder[0]][2] == pytest.approx(1.426)
    collar = [i for i, p in enumerate(original)
              if abs(p[0] - 0.058 * 1.7) < 1e-9
              and abs(p[1]) < 1e-9 and abs(p[2] - 0.85 * 1.7) < 1e-9]
    assert collar
    for i in collar:
        assert fitted[i] == pytest.approx(original[i])
