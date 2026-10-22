"""Opening classification must leave side edges stitched to both panels."""

from garment.reconstruction.mesh_builder import GarmentMeshBuilder


def _opening(point, garment_type, edge_vec, landmarks=None):
    return GarmentMeshBuilder._opening_name(
        point,
        garment_type,
        x0=0.0,
        x1=100.0,
        y0=0.0,
        y1=100.0,
        landmarks=landmarks or {},
        neck_opening=(50.0, 0.0, 10.0, 4.0, 100.0),
        edge_vec=edge_vec,
    )


def test_pants_hem_and_waist_keep_side_edges_closed_tc_gar_02() -> None:
    """TC-GAR-02: openings cross the leg or waist, not the vertical side."""
    assert _opening((80.0, 97.0), "pants", (5.0, 0.0)) == "right_hem"
    assert _opening((80.0, 97.0), "pants", (0.0, 5.0)) is None
    assert _opening((50.0, 3.0), "pants", (5.0, 0.0)) == "waist"
    assert _opening((50.0, 3.0), "pants", (0.0, 5.0)) is None


def test_tshirt_hem_and_cuff_keep_sleeve_side_closed_tc_gar_02() -> None:
    """TC-GAR-02: only the distal cuff and horizontal hem remain open."""
    landmarks = {
        "waist_left": (20.0, 70.0),
        "waist_right": (80.0, 70.0),
        "left_armpit": (25.0, 35.0),
        "right_armpit": (75.0, 35.0),
    }
    assert _opening((50.0, 98.0), "tshirt", (5.0, 0.0), landmarks) == "hem"
    assert _opening((50.0, 98.0), "tshirt", (0.0, 5.0), landmarks) is None
    assert _opening((99.0, 30.0), "tshirt", (0.0, 5.0), landmarks) == "right_cuff"
    assert _opening((84.0, 30.0), "tshirt", (0.0, 5.0), landmarks) is None
