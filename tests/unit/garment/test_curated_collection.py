"""TC-GAR-02: curated product metadata and safe selective asset installation."""

from io import BytesIO
import json
from zipfile import ZipFile

import pytest

from garment.mpfb import remote_pack
from garment.mpfb.catalog import DEFAULT_CATALOG
from garment.mpfb.install_collection import MANIFEST
from garment.mpfb.setup import extract_pack


def test_curated_counts_and_retained_products_tc_gar_02():
    """Test Case ID: TC-GAR-02. Preserve three originals and add 20 unique assets."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    catalog = json.loads(DEFAULT_CATALOG.read_text(encoding="utf-8"))["garments"]
    collection = [item for item in catalog if item.get("collection") == manifest["collection"]]
    retained = {item["id"] for item in catalog if item not in collection}
    assert retained == {"mpfb-aotest-hoodie", "mpfb-tshirt", "mpfb-pants"}
    assert len(catalog) == len({item["assets"][0] for item in catalog}) == 23
    assert len(collection) == len(manifest["products"]) == 20
    assert sum(item["category"] == "pants" for item in collection) == 10
    assert sum(item["category"] != "pants" for item in collection) == 10
    public = DEFAULT_CATALOG.parents[2] / "frontend/public"
    for item in catalog:
        preview = public / item["thumbnail_url"].lstrip("/")
        assert preview.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
        assert item["author"] and item["license"]
        assert item["sizes"] == ["M"]


def test_selective_extraction_keeps_complete_asset_tc_gar_02(tmp_path):
    """Test Case ID: TC-GAR-02. Select one asset with dependencies, skip other assets."""
    archive = tmp_path / "pack.zip"
    with ZipFile(archive, "w") as bundle:
        bundle.writestr("clothes/top/top.mhclo", "obj_file top.obj\nverts 0\n0\n")
        bundle.writestr("clothes/top/top.obj", "v 0 0 0\n")
        bundle.writestr("clothes/top/top.thumb", b"preview")
        bundle.writestr("clothes/other/other.mhclo", "verts 0\n0\n")
    destination = tmp_path / "installed"
    receipt = extract_pack(archive, destination, asset_names=["top"])
    assert len(receipt) == 3
    assert (destination / "clothes/top/top.obj").is_file()
    assert not (destination / "clothes/other").exists()


def test_selective_extraction_rejects_traversal_tc_gar_02(tmp_path):
    """Test Case ID: TC-GAR-02. Reject a selected directory containing path traversal."""
    archive = tmp_path / "bad.zip"
    with ZipFile(archive, "w") as bundle:
        bundle.writestr("clothes/top/top.mhclo", "verts 0\n0\n")
        bundle.writestr("clothes/top/../../../escape.obj", "bad")
    destination = tmp_path / "installed"
    with pytest.raises(ValueError):
        extract_pack(archive, destination, asset_names=["top"])
    assert not destination.exists()


def test_remote_zip_selects_members_without_network_tc_gar_02(tmp_path, monkeypatch):
    """Test Case ID: TC-GAR-02. Use ZIP metadata and CRC reads to fetch selected files only."""
    content = BytesIO()
    with ZipFile(content, "w") as bundle:
        bundle.writestr("clothes/top/top.mhclo", "verts 0\n0\n")
        bundle.writestr("clothes/top/top.obj", "v 0 0 0\n")
        bundle.writestr("clothes/other/other.mhclo", "excluded")
    payload = content.getvalue()

    class MemoryPack(BytesIO):
        def __init__(self, url, workspace):
            super().__init__(payload)
            self.size = len(payload)

    monkeypatch.setattr(remote_pack, "RemotePack", MemoryPack)
    target = tmp_path / "selected.zip"
    remote_pack.download_selected("https://example.invalid/mock.zip", target, ["top"])
    with ZipFile(target) as bundle:
        assert set(bundle.namelist()) == {"clothes/top/top.mhclo", "clothes/top/top.obj"}
        assert bundle.read("clothes/top/top.obj") == b"v 0 0 0\n"
