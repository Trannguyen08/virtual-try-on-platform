"""TC-GAR-02: local ZIP import, no downloads or Blender execution."""

from zipfile import ZipFile

import pytest

from garment.mpfb.setup import PackLinks, extract_pack


def test_zip_import_idempotent_and_preserves_local_edits_tc_gar_02(tmp_path):
    """Test Case ID: TC-GAR-02. Reinstall identical files; preserve local edits."""
    archive = tmp_path / "pack.zip"
    with ZipFile(archive, "w") as bundle:
        bundle.writestr("clothes/shirt/shirt.mhclo", "obj_file shirt.obj\nverts 0\n0\n")
        bundle.writestr("clothes/shirt/shirt.obj", "v 0 0 0\n")
        bundle.writestr("unexpected.py", "raise RuntimeError('must never execute')")
    destination = tmp_path / "assets"
    first = extract_pack(archive, destination)
    assert extract_pack(archive, destination) == first
    assert not (destination / "unexpected.py").exists()
    mesh = destination / "clothes/shirt/shirt.obj"
    mesh.write_text("edited locally", encoding="utf-8")
    with pytest.raises(ValueError, match="khác pack"):
        extract_pack(archive, destination)
    assert mesh.read_text(encoding="utf-8") == "edited locally"


@pytest.mark.parametrize("filename", ["../escape.obj", "C:/escape.obj", "folder\\escape.obj"])
def test_zip_path_validation_happens_before_write_tc_gar_02(tmp_path, filename):
    """Test Case ID: TC-GAR-02. Invalid archive does not write valid siblings."""
    archive = tmp_path / "bad.zip"
    with ZipFile(archive, "w") as bundle:
        bundle.writestr("valid.mhclo", "verts 0\n0\n")
        bundle.writestr(filename, "invalid")
    destination = tmp_path / "assets"
    with pytest.raises(ValueError):
        extract_pack(archive, destination)
    assert not destination.exists()


def test_pack_links_use_official_mirrors_only_tc_gar_02():
    """Test Case ID: TC-GAR-02. Resolve official ZIP mirrors without network."""
    parser = PackLinks()
    parser.feed('<a href="https://files2.makehumancommunity.org/assetpacks/example.zip">pack</a>'
                '<a href="https://example.org/other.zip">other</a>')
    assert parser.urls == ["https://files2.makehumancommunity.org/assetpacks/example.zip"]
