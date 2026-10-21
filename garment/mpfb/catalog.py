"""Validated MHCLO catalog usable by both FastAPI and Blender's Python.

No Blender imports, network access or third-party dependencies here.
"""

import json
import math
import os
from pathlib import Path, PureWindowsPath
import re
import struct


REPO = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = Path(__file__).with_name("catalog.json")
CATEGORIES = {"t_shirt", "shirt", "pants", "dress", "jacket"}
SIZES = {"XS", "S", "M", "L", "XL", "XXL"}


class GarmentConfigError(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def configured_path(variable, default):
    path = Path(os.environ.get(variable) or default).expanduser()
    return (path if path.is_absolute() else REPO / path).resolve()


def asset_root():
    return configured_path("MPFB_ASSET_ROOT", REPO / "data/external/mpfb")


def load_catalog(path=None):
    path = Path(path) if path else configured_path("MPFB_GARMENT_CATALOG", DEFAULT_CATALOG)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise GarmentConfigError("MHCLO_CATALOG_INVALID", "Không đọc được catalog MHCLO.") from exc
    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("garments"), list):
        raise GarmentConfigError("MHCLO_CATALOG_INVALID", "Catalog MHCLO cần version 1 và danh sách garments.")
    result = {}
    for item in data["garments"]:
        if not isinstance(item, dict):
            raise GarmentConfigError("MHCLO_CATALOG_INVALID", "Mỗi garment phải là một object.")
        identifier = item.get("id")
        assets, sizes = item.get("assets"), item.get("sizes")
        if (not isinstance(identifier, str) or not re.fullmatch(r"[a-z0-9_-]{1,64}", identifier)
                or identifier in result or not isinstance(item.get("category"), str)
                or item["category"] not in CATEGORIES
                or not isinstance(item.get("name"), str) or not item["name"].strip()
                or not isinstance(assets, list) or not assets
                or not all(isinstance(a, str) and re.fullmatch(r"[A-Za-z0-9_-]+", a) for a in assets)
                or len(assets) != len(set(assets))
                or not isinstance(sizes, list) or not sizes
                or not all(isinstance(s, str) and s in SIZES for s in sizes)
                or len(sizes) != len(set(sizes))
                or not isinstance(item.get("source"), str) or not item["source"].strip()
                or ("gender" in item and item["gender"] not in ("menswear", "womenswear", "unisex"))
                or not isinstance(item.get("license"), str) or not item["license"].strip()):
            raise GarmentConfigError("MHCLO_CATALOG_INVALID", "Garment MHCLO thiếu metadata hoặc có giá trị không hợp lệ.")
        engine = item.get("engine", "mhclo")
        if engine not in ("mhclo", "gltf_reference"):
            raise GarmentConfigError("MHCLO_CATALOG_INVALID", "Engine trang phục không được hỗ trợ.")
        if engine == "gltf_reference":
            height = item.get("reference_height_cm")
            offset = item.get("offset_m", [0, 0, 0])
            yaw = item.get("yaw_degrees", 0)
            if (not isinstance(height, (int, float)) or not math.isfinite(height) or not 100 <= height <= 250
                    or not isinstance(offset, list) or len(offset) != 3
                    or not all(isinstance(v, (int, float)) and math.isfinite(v) and abs(v) <= 2 for v in offset)
                    or not isinstance(yaw, (int, float)) or not math.isfinite(yaw)):
                raise GarmentConfigError("MHCLO_CATALOG_INVALID", "Cấu hình căn trang phục tham chiếu không hợp lệ.")
        result[identifier] = item
    return result


def validate_choice(entry, category, size):
    if entry["category"] != category:
        raise GarmentConfigError("MHCLO_CATEGORY_MISMATCH", "Loại trang phục không khớp catalog MHCLO.")
    if size not in entry["sizes"]:
        raise GarmentConfigError("SIZE_NOT_AVAILABLE", "Trang phục chưa hỗ trợ size được chọn; bản refit mẫu dùng M.")


def contained_file(root, base, reference):
    if (not reference or Path(reference).is_absolute()
            or PureWindowsPath(reference).drive or "\\" in reference):
        raise GarmentConfigError("MHCLO_ASSET_INVALID", "Đường dẫn asset phải tương đối trong kho MHCLO.")
    path = (base / reference).resolve()
    if not path.is_relative_to(root.resolve()):
        raise GarmentConfigError("MHCLO_ASSET_INVALID", "Asset tham chiếu file ngoài kho MHCLO.")
    if not path.is_file():
        raise GarmentConfigError("MHCLO_ASSET_MISSING", "Asset MHCLO thiếu mesh, material hoặc texture đi kèm.")
    return path


def asset_dependencies(path, root):
    """Verify local mesh/material/texture references before invoking Blender."""
    references = {}
    files = [path]
    has_mapping = False
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        words = line.strip().split(maxsplit=1)
        if len(words) == 2 and words[0] in {"obj_file", "material"}:
            references[words[0]] = words[1]
        if words and words[0] == "verts":
            has_mapping = True
    if "obj_file" not in references or not has_mapping:
        raise GarmentConfigError("MHCLO_ASSET_INVALID", "MHCLO thiếu obj_file hoặc mapping verts.")
    mesh = contained_file(root, path.parent, references["obj_file"])
    files.append(mesh)
    if mesh.suffix.lower() != ".obj":
        raise GarmentConfigError("MHCLO_ASSET_INVALID", "Mesh MHCLO phải là OBJ.")
    if "material" in references:
        material = contained_file(root, path.parent, references["material"])
        files.append(material)
        for line in material.read_text(encoding="utf-8-sig").splitlines():
            words = line.strip().split(maxsplit=1)
            if (len(words) == 2 and words[0].lower().endswith("texture")
                    and words[1].lower() not in {"none", "null"}):
                files.append(contained_file(root, material.parent, words[1]))
    return sorted(set(files))


def resolve_assets(entry, root=None):
    root = Path(root or asset_root()).resolve()
    external = entry.get("engine") == "gltf_reference"
    paths = list(root.rglob("*.glb" if external else "*.mhclo")) if root.is_dir() else []
    result = []
    for name in entry["assets"]:
        matches = [p.resolve() for p in paths if p.stem == name or p.parent.name == name]
        matches = sorted(set(matches))
        if not matches:
            raise GarmentConfigError("MHCLO_ASSET_MISSING", f"Chưa cài asset {name}. Chạy bước cài quần áo MPFB mẫu.")
        if len(matches) != 1:
            raise GarmentConfigError("MHCLO_ASSET_AMBIGUOUS", f"Asset {name} có nhiều bản; chỉ giữ một bản trong kho đang dùng.")
        path = matches[0]
        if not path.is_relative_to(root):
            raise GarmentConfigError("MHCLO_ASSET_INVALID", "Asset MHCLO nằm ngoài kho cấu hình.")
        try:
            if external:
                with path.open("rb") as stream:
                    header = stream.read(12)
                if len(header) != 12 or struct.unpack("<4sII", header) != (b"glTF", 2, path.stat().st_size):
                    raise GarmentConfigError("MHCLO_ASSET_INVALID", "GLB trang phục không hợp lệ.")
                report_file = path.with_suffix(".prepared.json")
                if not report_file.is_file():
                    raise GarmentConfigError("MHCLO_ASSET_MISSING", "Thiếu báo cáo chuẩn hóa GLB trang phục.")
                preparation = json.loads(report_file.read_text(encoding="utf-8"))
                if not isinstance(preparation, dict) or preparation.get("units") != "m" or preparation.get("up") != "Y":
                    raise GarmentConfigError("MHCLO_ASSET_INVALID", "GLB chưa được chuẩn hóa mét/Y-up.")
            else:
                asset_dependencies(path, root)
        except GarmentConfigError:
            raise
        except (OSError, UnicodeError, ValueError) as exc:
            raise GarmentConfigError("MHCLO_ASSET_INVALID", "Không đọc được file tham chiếu của asset MHCLO.") from exc
        result.append(path)
    return result


def catalog_status():
    items = []
    for entry in load_catalog().values():
        try:
            resolve_assets(entry)
            available, error = True, None
        except (GarmentConfigError, OSError, UnicodeError) as exc:
            available = False
            error = exc.code if isinstance(exc, GarmentConfigError) else "MHCLO_ASSET_INVALID"
        mode = "reference_alignment" if entry.get("engine") == "gltf_reference" else "body_refit"
        items.append({**entry, "available": available, "error_code": error,
                      "mode": mode, "size_chart_verified": False})
    return items
