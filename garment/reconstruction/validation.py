from __future__ import annotations

import json
import struct
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

from .contracts import MeshMetadata
from .errors import InvalidMeshError

GLB_MAGIC = b"glTF"
JSON_CHUNK = 0x4E4F534A


class GlbValidator:
    def __init__(self, *, max_file_bytes: int = 50 * 1024 * 1024) -> None:
        self.max_file_bytes = max_file_bytes

    def validate(self, path: Path) -> MeshMetadata:
        file_size = path.stat().st_size
        if file_size < 20 or file_size > self.max_file_bytes:
            raise InvalidMeshError("GLB size is outside the accepted range")

        with path.open("rb") as stream:
            header = stream.read(12)
            magic, version, declared_length = struct.unpack("<4sII", header)
            if magic != GLB_MAGIC or version != 2 or declared_length != file_size:
                raise InvalidMeshError("Invalid GLB header")
            chunk_header = stream.read(8)
            if len(chunk_header) != 8:
                raise InvalidMeshError("GLB is missing its JSON chunk")
            chunk_length, chunk_type = struct.unpack("<II", chunk_header)
            if chunk_type != JSON_CHUNK or chunk_length > file_size - 20:
                raise InvalidMeshError("Invalid GLB JSON chunk")
            try:
                document = json.loads(
                    stream.read(chunk_length).decode("utf-8").rstrip(" \t\r\n\x00")
                )
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise InvalidMeshError("GLB contains invalid JSON") from exc

        asset_version = str(document.get("asset", {}).get("version", ""))
        if not asset_version.startswith("2"):
            raise InvalidMeshError("Only glTF 2.x assets are supported")

        meshes = document.get("meshes") or []
        primitives = [
            primitive for mesh in meshes for primitive in mesh.get("primitives", [])
        ]
        if not meshes or not primitives:
            raise InvalidMeshError("GLB does not contain a mesh primitive")

        self._reject_external_references(document)
        triangle_count = self._triangle_count(document, primitives)
        materials = document.get("materials") or []
        textures = document.get("textures") or []
        has_pbr = any("pbrMetallicRoughness" in material for material in materials)
        return MeshMetadata(
            file_size_bytes=file_size,
            mesh_count=len(meshes),
            primitive_count=len(primitives),
            triangle_count=triangle_count,
            material_count=len(materials),
            texture_count=len(textures),
            has_pbr_material=has_pbr,
        )

    @staticmethod
    def _reject_external_references(document: dict) -> None:
        for collection in (document.get("buffers", []), document.get("images", [])):
            for item in collection:
                uri = item.get("uri")
                if not uri or uri.startswith("data:"):
                    continue
                parsed = urlparse(uri)
                if (
                    parsed.scheme
                    or parsed.netloc
                    or ".." in PurePosixPath(parsed.path).parts
                ):
                    raise InvalidMeshError("GLB contains an unsafe external reference")
                raise InvalidMeshError("GLB must embed all buffers and images")

    @staticmethod
    def _triangle_count(document: dict, primitives: list[dict]) -> int | None:
        accessors = document.get("accessors") or []
        total = 0
        for primitive in primitives:
            mode = primitive.get("mode", 4)
            if mode != 4:
                return None
            accessor_index = primitive.get("indices")
            if accessor_index is None:
                accessor_index = primitive.get("attributes", {}).get("POSITION")
            if not isinstance(accessor_index, int) or not 0 <= accessor_index < len(
                accessors
            ):
                return None
            count = accessors[accessor_index].get("count")
            if not isinstance(count, int):
                return None
            total += count // 3
        return total
