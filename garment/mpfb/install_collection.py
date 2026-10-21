"""Install the curated 10 tops / 10 trousers with their authentic thumbnails.

Run explicitly: python -m garment.mpfb.install_collection
Existing assets are validated and reused; importing this module does no I/O.
"""

import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from .catalog import DEFAULT_CATALOG, REPO, asset_root, asset_dependencies, resolve_assets
from .setup import download_pack, extract_pack
from .remote_pack import download_selected

MANIFEST = Path(__file__).with_name("collection.json")


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def install():
    collection = json.loads(MANIFEST.read_text(encoding="utf-8"))
    products = collection["products"]
    if (len(products) != 20 or sum(p["category"] == "pants" for p in products) != 10
            or len({p["id"] for p in products}) != 20
            or len({p["asset"] for p in products}) != 20):
        raise ValueError("Collection must contain 10 unique tops and 10 unique trousers")
    root = asset_root()
    root.mkdir(parents=True, exist_ok=True)
    receipts = []
    for pack, page in collection["packs"].items():
        entries = [p for p in products if p["pack"] == pack]
        missing = []
        for item in entries:
            try:
                resolve_assets({"assets": [item["asset"]]}, root)
            except ValueError:
                missing.append(item["asset"])
        if not missing:
            print(f"Reusing {pack}: {len(entries)} validated assets", flush=True)
            continue
        with tempfile.TemporaryDirectory(prefix=".collection-", dir=root) as directory:
            archive = Path(directory) / f"{pack}.zip"
            print(f"Downloading {pack} for {len(missing)} assets...", flush=True)
            cached = root / f"{pack}-selected-source.zip"
            source_url = collection.get("downloads", {}).get(pack)
            if cached.is_file():
                archive = cached
                source = source_url or page
            elif source_url:
                source = download_selected(source_url, archive, missing)
            else:
                source = download_pack(page, archive, max_bytes=192 * 1024 * 1024)
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            files = extract_pack(archive, root / pack, asset_names=missing)
            receipt = {"pack": pack, "page": page, "source": source,
                       "archive_sha256": digest, "selected_assets": missing, "files": files}
            write_json(root / f"{pack}.collection.receipt.json", receipt)
            receipts.append({"pack": pack, "archive_sha256": digest})
            print(f"Installed {pack}: {len(files)} files", flush=True)

    thumbnails = REPO / "frontend/public/images/makehuman"
    thumbnails.mkdir(parents=True, exist_ok=True)
    catalog = json.loads(DEFAULT_CATALOG.read_text(encoding="utf-8"))
    keep_ids = {"mpfb-aotest-hoodie", "mpfb-tshirt", "mpfb-pants"}
    entries_by_id = {entry["id"]: entry for entry in catalog["garments"] if entry["id"] in keep_ids}
    if set(entries_by_id) != keep_ids:
        raise ValueError("The three products requested for preservation must exist in the catalog")
    attribution = []
    for item in products:
        path = resolve_assets({"assets": [item["asset"]]}, root)[0]
        preview = path.with_suffix(".thumb")
        if not preview.is_file() or preview.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Missing authentic PNG preview for {item['asset']}")
        image_name = f"{item['asset']}.png"
        shutil.copyfile(preview, thumbnails / image_name)
        page = collection["packs"][item["pack"]]
        entry = {key: item[key] for key in ("id", "name", "category", "gender", "author", "license")}
        entry.update({"engine": "mhclo", "sizes": ["M"], "assets": [item["asset"]],
                      "source": page, "collection": collection["collection"],
                      "thumbnail_url": f"/images/makehuman/{image_name}",
                      "thumbnail_source": f"https://static.makehumancommunity.org/assets/assetpacks/{image_name}"})
        entries_by_id[item["id"]] = entry
        attribution.append({**entry, "thumbnail_sha256": hashlib.sha256(preview.read_bytes()).hexdigest(),
                            "asset_files": [{"file": p.relative_to(root).as_posix(),
                                             "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                                            for p in asset_dependencies(path, root)]})
    # Keep legacy names/IDs intact and attach exact previews where available.
    for identifier in ("mpfb-aotest-hoodie", "mpfb-tshirt", "mpfb-pants"):
        entry = entries_by_id[identifier]
        path = resolve_assets(entry, root)[0]
        preview = path.with_suffix(".thumb")
        if identifier == "mpfb-aotest-hoodie" and not preview.is_file():
            preview = REPO / "data/external/aotest/ladieshoodiedown1.thumb"
        if not preview.is_file():
            raise ValueError(f"Missing preview for retained product {identifier}")
        if preview.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Preview is not PNG for retained product {identifier}")
        image_name = f"{path.stem}.png"
        shutil.copyfile(preview, thumbnails / image_name)
        entry["thumbnail_url"] = f"/images/makehuman/{image_name}"
        entry["author"] = {"mpfb-aotest-hoodie": "Elvaerwyn", "mpfb-tshirt": "MargaretToigo", "mpfb-pants": "Cortu"}[identifier]
        entry["thumbnail_source"] = str(preview.relative_to(REPO)).replace("\\", "/") if identifier == "mpfb-aotest-hoodie" else f"https://static.makehumancommunity.org/assets/assetpacks/{image_name}"
        attribution.append({**entry, "thumbnail_sha256": hashlib.sha256(preview.read_bytes()).hexdigest()})
    catalog["garments"] = list(entries_by_id.values())
    if len(catalog["garments"]) != 23 or len({entry["assets"][0] for entry in catalog["garments"]}) != 23:
        raise ValueError("Catalog must contain exactly 23 distinct assets")
    for entry in catalog["garments"]:
        resolve_assets(entry, root)
        if not (REPO / "frontend/public" / entry["thumbnail_url"].lstrip("/")).is_file():
            raise ValueError(f"Missing product preview: {entry['id']}")
    write_json(DEFAULT_CATALOG, catalog)
    # This small file accompanies the distributed screenshots and preserves credits.
    write_json(thumbnails / "ATTRIBUTION.json", {
        "source": "https://static.makehumancommunity.org/assets/assetpacks.html",
        "collection": collection["collection"],
        "note": "Original asset previews. No synthetic product photography or verified retail sizes/prices.",
        "products": [{key: entry[key] for key in ("id", "name", "author", "license", "source", "thumbnail_url", "thumbnail_source", "thumbnail_sha256")} for entry in attribution],
    })
    write_json(root / "collection.receipt.json", {"products": attribution, "downloads": receipts})
    print("Catalog ready: 3 retained + 10 new tops + 10 new trousers = 23 products.", flush=True)


if __name__ == "__main__":
    install()
