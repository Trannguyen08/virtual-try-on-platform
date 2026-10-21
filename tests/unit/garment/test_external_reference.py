"""Reference alignment remains distinct from anatomical refitting."""

import json
import struct

import pytest

from garment.external.alignment import reference_scale
from garment.mpfb.catalog import GarmentConfigError, resolve_assets


def test_tc_ext_001_height_scale():
    assert reference_scale(1.62, 180) == pytest.approx(0.9)


@pytest.mark.parametrize("height,reference", [(0, 180), (1.8, 0), (float("nan"), 180)])
def test_tc_ext_002_invalid_height(height, reference):
    with pytest.raises(ValueError):
        reference_scale(height, reference)


@pytest.mark.parametrize("report", ["{broken", "[]", '{"units":"cm","up":"Y"}'])
def test_tc_ext_003_bad_preparation_report(tmp_path, report):
    asset = tmp_path / "sample.glb"
    asset.write_bytes(struct.pack("<4sII", b"glTF", 2, 12))
    asset.with_suffix(".prepared.json").write_text(report, encoding="utf-8")
    with pytest.raises(GarmentConfigError) as caught:
        resolve_assets({"engine": "gltf_reference", "assets": ["sample"]}, tmp_path)
    assert caught.value.code == "MHCLO_ASSET_INVALID"


def test_tc_ext_004_prepared_asset_discovery(tmp_path):
    # This exercises catalog discovery only, not full glTF validation or rendering.
    asset = tmp_path / "sample.glb"
    asset.write_bytes(struct.pack("<4sII", b"glTF", 2, 12))
    asset.with_suffix(".prepared.json").write_text(
        json.dumps({"units": "m", "up": "Y"}), encoding="utf-8")
    assert resolve_assets({"engine": "gltf_reference", "assets": ["sample"]}, tmp_path) == [asset]
