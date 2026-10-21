"""MHCLO/MPFB topology compatibility checks without importing Blender."""

from types import SimpleNamespace

import pytest

from garment.mpfb.blender_fitting import validate_mapping


def mapping_fixture():
    return SimpleNamespace(
        verts={0: {"verts": (0, 1, 2), "weights": (1, 0, 0), "offsets": (0, 0, 0)}},
        x_scale=(0, 1, 1), y_scale=None, z_scale=None,
    )


def test_compatible_mapping_is_accepted_tc_gar_02():
    """Test Case ID: TC-GAR-02. Known indices and full vertex coverage pass."""
    validate_mapping(mapping_fixture(), 3, 1)


@pytest.mark.parametrize("body_count,garment_count", [(2, 1), (3, 2)])
def test_missing_body_or_garment_vertex_is_not_skipped_tc_gar_02(body_count, garment_count):
    """Test Case ID: TC-GAR-02. Reject mismatch before presenting a fitted mesh."""
    with pytest.raises(ValueError, match="MHCLO_TOPOLOGY_MISMATCH"):
        validate_mapping(mapping_fixture(), body_count, garment_count)


def test_invalid_scaling_or_nan_cannot_reach_fitting_tc_gar_02():
    """Test Case ID: TC-GAR-02. Reject divide-by-zero and non-finite geometry."""
    mapping = mapping_fixture()
    mapping.x_scale = (0, 1, 0)
    with pytest.raises(ValueError, match="scale references"):
        validate_mapping(mapping, 3)
    mapping.x_scale = None
    mapping.verts[0]["offsets"] = (float("nan"), 0, 0)
    with pytest.raises(ValueError, match="non-finite"):
        validate_mapping(mapping, 3)
