from pathlib import Path

import pytest

from garment.reconstruction.errors import InvalidMeshError
from garment.reconstruction.providers.mock import build_mock_glb
from garment.reconstruction.validation import GlbValidator


def test_validator_reads_minimal_glb_metadata(tmp_path: Path) -> None:
    path = tmp_path / "model.glb"
    path.write_bytes(build_mock_glb())

    metadata = GlbValidator().validate(path)

    assert metadata.mesh_count == 1
    assert metadata.primitive_count == 1
    assert metadata.triangle_count == 1
    assert metadata.has_pbr_material is True


def test_validator_rejects_invalid_glb(tmp_path: Path) -> None:
    path = tmp_path / "invalid.glb"
    path.write_bytes(b"not a glb")
    with pytest.raises(InvalidMeshError):
        GlbValidator().validate(path)
