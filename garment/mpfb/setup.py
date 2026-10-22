"""User-run installation/check command. Importing this module never downloads.

python -m garment.mpfb.setup --download-demo
python -m garment.mpfb.setup --shirts-zip C:/Downloads/shirts01.zip --pants-zip ...
python -m garment.mpfb.setup --check
"""

import argparse
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import stat
import sys
import tempfile
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from zipfile import BadZipFile, ZipFile

from .catalog import GarmentConfigError, asset_root, catalog_status


PAGES = {
    "shirts01": "https://static.makehumancommunity.org/assets/assetpacks/shirts01.html",
    "pants01": "https://static.makehumancommunity.org/assets/assetpacks/pants01.html",
}
MAX_DOWNLOAD = 64 * 1024 * 1024
MAX_EXPANDED = 256 * 1024 * 1024
EXTENSIONS = {".mhclo", ".obj", ".mhmat", ".png", ".jpg", ".jpeg", ".thumb",
              ".txt", ".json", ".mhw", ".mpfbskel", ".license"}


class PackLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href", "")
            parsed = urlparse(href)
            if (parsed.scheme in {"https", "http"} and parsed.hostname in {
                    "files2.makehumancommunity.org", "files.makehumancommunity.org"}
                    and parsed.path.lower().endswith(".zip")):
                self.urls.append(parsed._replace(scheme="https").geturl())


def download_pack(page, target, max_bytes=MAX_DOWNLOAD):
    request = Request(page, headers={"User-Agent": "VirtualTryOn-MPFB-setup/1"})
    with urlopen(request, timeout=60) as response:
        markup = response.read(2 * 1024 * 1024).decode("utf-8")
    parser = PackLinks()
    parser.feed(markup)
    if not parser.urls:
        raise ValueError("Trang asset không có link ZIP được hỗ trợ; tải ZIP từ trang chính thức rồi dùng --shirts-zip/--pants-zip.")
    last_error = None
    for url in dict.fromkeys(parser.urls):
        try:
            request = Request(urljoin(page, url), headers={"User-Agent": "VirtualTryOn-MPFB-setup/1"})
            size = 0
            with urlopen(request, timeout=60) as response, target.open("wb") as stream:
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    if size > max_bytes:
                        raise ValueError(f"Asset pack vượt giới hạn tải {max_bytes // (1024 * 1024)} MiB.")
                    stream.write(chunk)
            return url
        except (OSError, ValueError) as exc:
            last_error = exc
    raise ValueError("Không tải được pack từ mirror chính thức; dùng file ZIP tải thủ công.") from last_error


def extract_pack(archive, destination, asset_names=None):
    """Validate all members first; never execute pack contents or replace edits."""
    destination = Path(destination).resolve()
    with ZipFile(archive) as bundle:
        members = bundle.infolist()
        if asset_names is not None:
            selected = set(asset_names)
            members = [member for member in members
                       if selected.intersection(PurePosixPath(member.filename).parts)]
        if len(members) > 5000 or sum(m.file_size for m in members) > MAX_EXPANDED:
            raise ValueError("Asset pack vượt giới hạn giải nén.")
        planned, seen = [], set()
        for member in members:
            relative = PurePosixPath(member.filename)
            mode = member.external_attr >> 16
            if (relative.is_absolute() or PureWindowsPath(member.filename).drive
                    or ".." in relative.parts or "\\" in member.filename
                    or stat.S_ISLNK(mode)):
                raise ValueError("Asset pack có đường dẫn không hợp lệ.")
            target = (destination / member.filename).resolve()
            if not target.is_relative_to(destination):
                raise ValueError("Asset pack tham chiếu ngoài thư mục cài.")
            if member.is_dir() or target.suffix.lower() not in EXTENSIONS:
                continue
            key = str(target).casefold()
            if key in seen:
                raise ValueError("Asset pack có file trùng tên.")
            seen.add(key)
            planned.append((member, target))
        if not any(target.suffix.lower() == ".mhclo" for _, target in planned):
            raise ValueError("Asset pack không có file MHCLO.")
        receipt = []
        for member, target in planned:
            content = bundle.read(member)
            digest = hashlib.sha256(content).hexdigest()
            if target.exists():
                if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                    raise ValueError("File asset hiện tại khác pack; giữ lại file và dùng MPFB_ASSET_ROOT mới để cài.")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            receipt.append({"file": target.relative_to(destination).as_posix(), "sha256": digest})
    return receipt


def main():
    parser = argparse.ArgumentParser(description="Cài/check quần áo mẫu MPFB cho dự án")
    parser.add_argument("--download-demo", action="store_true")
    parser.add_argument("--shirts-zip", type=Path)
    parser.add_argument("--pants-zip", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--asset-root", type=Path)
    parser.add_argument("--catalog", type=Path)
    args = parser.parse_args()
    if args.asset_root:
        os.environ["MPFB_ASSET_ROOT"] = str(args.asset_root)
    if args.catalog:
        os.environ["MPFB_GARMENT_CATALOG"] = str(args.catalog)
    root = asset_root()
    if args.download_demo or args.shirts_zip or args.pants_zip:
        root.mkdir(parents=True, exist_ok=True)
        for name, local in (("shirts01", args.shirts_zip), ("pants01", args.pants_zip)):
            if not args.download_demo and local is None:
                continue
            with tempfile.TemporaryDirectory(prefix=".install-", dir=root) as temporary:
                archive = local or Path(temporary) / f"{name}.zip"
                source = "user-provided-zip"
                if local is None:
                    print(f"Đang tải {name} từ trang MakeHuman chính thức...", flush=True)
                    source = download_pack(PAGES[name], archive)
                files = extract_pack(archive, root / name)
                receipt = {"pack": name, "page": PAGES[name], "source": source,
                           "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                           "files": files}
                (root / f"{name}.receipt.json").write_text(
                    json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"Đã cài {name}: {len(files)} file.")
    statuses = catalog_status()
    for item in statuses:
        state = "SẴN SÀNG" if item["available"] else item["error_code"]
        print(f"{item['id']}: {state}")
    return 0 if all(item["available"] for item in statuses) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (GarmentConfigError, OSError, ValueError, BadZipFile) as exc:
        print(f"Cài/check MPFB thất bại: {exc}", file=sys.stderr)
        sys.exit(1)
