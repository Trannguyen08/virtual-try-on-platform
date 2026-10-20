"""TC-GAR-02: operator asset validation without Blender/network."""

import json
import pytest

from garment.mpfb.catalog import (
    GarmentConfigError, asset_dependencies, catalog_status, contained_file,
    load_catalog, resolve_assets, validate_choice,
)


@pytest.fixture
def refit_library(tmp_path, monkeypatch):
    root = tmp_path / "assets"
    folder = root / "pack" / "sample_shirt"
    folder.mkdir(parents=True)
    mhclo = folder / "shirt.mhclo"
    mhclo.write_text("obj_file shirt.obj\nmaterial shirt.mhmat\nverts 0\n0\n", encoding="utf-8")
    (folder / "shirt.obj").write_text("v 0 0 0\n", encoding="utf-8")
    (folder / "shirt.mhmat").write_text("diffuseTexture fabric.png\n", encoding="utf-8")
    (folder / "fabric.png").write_bytes(b"fixture-not-a-real-texture")
    entry = {"id": "sample-shirt", "name": "Sample", "category": "t_shirt", "sizes": ["M"],
             "assets": ["sample_shirt"], "license": "CC0", "source": "test-fixture"}
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"version": 1, "garments": [entry]}), encoding="utf-8")
    monkeypatch.setenv("MPFB_GARMENT_CATALOG", str(catalog))
    monkeypatch.setenv("MPFB_ASSET_ROOT", str(root))
    return root, mhclo, entry, catalog


def test_asset_dependencies_and_status_tc_gar_02(refit_library):
    """Test Case ID: TC-GAR-02. Assets resolve with all local dependencies."""
    root, path, entry, _ = refit_library
    assert load_catalog()[entry["id"]] == entry
    assert resolve_assets(entry) == [path]
    assert {p.suffix for p in asset_dependencies(path, root)} == {".mhclo", ".obj", ".mhmat", ".png"}
    status = catalog_status()[0]
    assert status["available"] is True
    assert status["size_chart_verified"] is False
    assert str(root) not in json.dumps(status)


def test_missing_texture_is_unavailable_not_synthetic_success_tc_gar_02(refit_library):
    """Test Case ID: TC-GAR-02. Missing texture blocks fitting explicitly."""
    _, path, _, _ = refit_library
    (path.parent / "fabric.png").unlink()
    status = catalog_status()[0]
    assert status["available"] is False
    assert status["error_code"] == "MHCLO_ASSET_MISSING"


@pytest.mark.parametrize("reference", ["../outside.obj", "C:/private.obj", "C:private.obj", "/etc/passwd"])
def test_asset_reference_cannot_escape_root_tc_gar_02(tmp_path, reference):
    """Test Case ID: TC-GAR-02. Outside/drive-relative dependency is rejected."""
    root = tmp_path / "assets"
    root.mkdir()
    with pytest.raises(GarmentConfigError) as error:
        contained_file(root, root, reference)
    assert error.value.code == "MHCLO_ASSET_INVALID"


def test_ambiguous_asset_is_rejected_tc_gar_02(refit_library):
    """Test Case ID: TC-GAR-02. Do not silently choose between asset versions."""
    root, _, entry, _ = refit_library
    duplicate = root / "other-pack" / "sample_shirt"
    duplicate.mkdir(parents=True)
    (duplicate / "duplicate.mhclo").write_text("verts 0\n0\n", encoding="utf-8")
    with pytest.raises(GarmentConfigError) as error:
        resolve_assets(entry)
    assert error.value.code == "MHCLO_ASSET_AMBIGUOUS"


@pytest.mark.parametrize("field,value", [("id", "../invalid"), ("category", []), ("sizes", ["?Size"]), ("assets", [])])
def test_invalid_catalog_is_structured_error_tc_gar_02(refit_library, field, value):
    """Test Case ID: TC-GAR-02. Invalid operator config returns a clear error."""
    _, _, entry, path = refit_library
    entry[field] = value
    path.write_text(json.dumps({"version": 1, "garments": [entry]}), encoding="utf-8")
    with pytest.raises(GarmentConfigError) as error:
        load_catalog()
    assert error.value.code == "MHCLO_CATALOG_INVALID"


def test_refit_does_not_claim_multiple_real_sizes_tc_gar_02(refit_library):
    """Test Case ID: TC-GAR-02. Unsupported size must not globally scale asset."""
    _, _, entry, _ = refit_library
    with pytest.raises(GarmentConfigError) as error:
        validate_choice(entry, "t_shirt", "L")
    assert error.value.code == "SIZE_NOT_AVAILABLE"
