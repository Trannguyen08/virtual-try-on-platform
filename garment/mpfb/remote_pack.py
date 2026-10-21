"""Read selected MakeHuman ZIP members with verified HTTPS byte ranges.

Only asset data is downloaded; archive contents are never executed.
"""

from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
from urllib.parse import urlparse
from zipfile import ZipFile, ZIP_DEFLATED


class RemotePack:
    def __init__(self, url, workspace):
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in {
            "files2.makehumancommunity.org", "files.makehumancommunity.org",
        } or not parsed.path.endswith(".zip"):
            raise ValueError("Only official HTTPS MakeHuman ZIP mirrors are supported")
        self.url = url
        self.workspace = Path(workspace)
        self.position = 0
        self.blocks = []
        payload, header = self.fetch("-131072")
        match = re.search(r"content-range:\s*bytes\s+(\d+)-(\d+)/(\d+)", header, re.I)
        if not match:
            raise ValueError("Asset server did not provide a ZIP byte range")
        start, end, self.size = map(int, match.groups())
        if len(payload) != end - start + 1 or self.size > 512 * 1024 * 1024:
            raise ValueError("Invalid or oversized asset pack response")
        self.blocks.append((start, payload))

    def fetch(self, requested_range):
        with tempfile.TemporaryDirectory(prefix="range-", dir=self.workspace) as directory:
            content = Path(directory) / "content"
            headers = Path(directory) / "headers"
            subprocess.run([
                "curl.exe", "--fail", "--silent", "--show-error", "--location",
                "--proto", "=https", "--connect-timeout", "15", "--max-time", "60",
                "--range", requested_range, "--dump-header", str(headers),
                "--output", str(content), self.url,
            ], check=True, timeout=65)
            return content.read_bytes(), headers.read_text(encoding="latin-1")

    def seek(self, offset, whence=0):
        position = offset if whence == 0 else self.position + offset if whence == 1 else self.size + offset
        if position < 0:
            raise ValueError("Invalid ZIP offset")
        self.position = position
        return position

    def tell(self):
        return self.position

    def seekable(self):
        return True

    def read(self, amount=-1):
        end = self.size if amount < 0 else min(self.size, self.position + amount)
        if end <= self.position:
            return b""
        for start, block in reversed(self.blocks):
            if start <= self.position and end <= start + len(block):
                result = block[self.position - start:end - start]
                self.position = end
                return result
        start = self.position
        payload, header = self.fetch(f"{start}-{end - 1}")
        if len(payload) != end - start or not re.search(
            rf"content-range:\s*bytes\s+{start}-{end - 1}/{self.size}", header, re.I,
        ):
            raise ValueError("ZIP range content does not match requested offsets")
        self.blocks.append((start, payload))
        self.position = end
        return payload


def download_selected(url, target, asset_names):
    """Create a small local ZIP containing complete selected asset directories."""
    remote = RemotePack(url, target.parent)
    with ZipFile(remote) as source:
        members = [entry for entry in source.infolist()
                   if set(asset_names).intersection(PurePosixPath(entry.filename).parts)]
        if not members or sum(entry.file_size for entry in members) > 256 * 1024 * 1024:
            raise ValueError("Selected asset files are missing or too large")
        for asset in asset_names:
            entries = [entry for entry in members if asset in PurePosixPath(entry.filename).parts]
            if not entries:
                raise ValueError(f"Asset directory not present in official ZIP: {asset}")
            start = min(entry.header_offset for entry in entries)
            end = min(remote.size, max(entry.header_offset + entry.compress_size + 65536 + 30
                                      + len(entry.filename.encode("utf-8")) for entry in entries))
            print(f"Fetching {asset}: {(end - start) / 1048576:.1f} MiB", flush=True)
            remote.seek(start)
            remote.read(end - start)
        with ZipFile(target, "w", compression=ZIP_DEFLATED) as output:
            for entry in members:
                output.writestr(entry, source.read(entry))
    return url
