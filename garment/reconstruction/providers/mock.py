from __future__ import annotations

import asyncio
import json
import shutil
import struct
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

from ..contracts import (
    GenerationRequest,
    ProviderResult,
    ProviderTask,
    ProviderTaskStatus,
    TaskState,
)
from ..errors import ProviderError


class MockGarment3DProvider:
    """Deterministic provider used by local development and CI."""

    name = "mock"

    def __init__(self, fixture_dir: Path) -> None:
        self.fixture_dir = fixture_dir
        self.fixture_dir.mkdir(parents=True, exist_ok=True)
        self.fixture_path = self.fixture_dir / "mock-garment.glb"
        if not self.fixture_path.exists():
            self.fixture_path.write_bytes(build_mock_glb())
        self._tasks: dict[str, GenerationRequest] = {}

    async def create_task(self, request: GenerationRequest) -> ProviderTask:
        digest = request.images[0].sha256[:20]
        external_id = f"mock_{digest}_{len(request.images)}"
        self._tasks[external_id] = request
        return ProviderTask(provider=self.name, external_id=external_id)

    async def get_task(self, external_id: str) -> ProviderTaskStatus:
        if not external_id.startswith("mock_"):
            raise ProviderError(
                "PROVIDER_TASK_NOT_FOUND", "Mock task was not found", http_status=404
            )
        return ProviderTaskStatus(
            state=TaskState.SUCCESS,
            progress=100,
            result=ProviderResult(
                model_url=self.fixture_path.as_uri(),
                metadata={"mock": True},
            ),
        )

    async def download(self, url: str, destination: Path, max_bytes: int) -> None:
        parsed = urlparse(url)
        source = (
            Path(url2pathname(unquote(parsed.path)))
            if parsed.scheme == "file"
            else Path(url)
        )
        if not source.exists() or source.stat().st_size > max_bytes:
            raise ProviderError(
                "PROVIDER_DOWNLOAD_FAILED", "Mock artifact is unavailable"
            )
        destination.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(shutil.copyfile, source, destination)

    async def cancel_task(self, external_id: str) -> bool:
        return self._tasks.pop(external_id, None) is not None

    async def close(self) -> None:
        return None


def build_mock_glb() -> bytes:
    """Build a tiny valid triangle GLB without third-party 3D dependencies."""
    document = {
        "asset": {"version": "2.0", "generator": "garment3d-mock"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "MockGarment"}],
        "meshes": [
            {
                "primitives": [
                    {"attributes": {"POSITION": 0}, "indices": 1, "material": 0}
                ]
            }
        ],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": 3,
                "type": "VEC3",
                "min": [-0.5, 0.0, 0.0],
                "max": [0.5, 1.0, 0.0],
            },
            {"bufferView": 1, "componentType": 5123, "count": 3, "type": "SCALAR"},
        ],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": 36, "target": 34962},
            {"buffer": 0, "byteOffset": 36, "byteLength": 6, "target": 34963},
        ],
        "buffers": [{"byteLength": 44}],
        "materials": [
            {"pbrMetallicRoughness": {"baseColorFactor": [0.2, 0.45, 0.9, 1.0]}}
        ],
    }
    json_chunk = json.dumps(document, separators=(",", ":")).encode("utf-8")
    json_chunk += b" " * ((4 - len(json_chunk) % 4) % 4)
    vertices = struct.pack("<9f", -0.5, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 1.0, 0.0)
    indices = struct.pack("<3H", 0, 1, 2)
    binary_chunk = vertices + indices
    binary_chunk += b"\x00" * ((4 - len(binary_chunk) % 4) % 4)
    total_length = 12 + 8 + len(json_chunk) + 8 + len(binary_chunk)
    return b"".join(
        (
            struct.pack("<4sII", b"glTF", 2, total_length),
            struct.pack("<II", len(json_chunk), 0x4E4F534A),
            json_chunk,
            struct.pack("<II", len(binary_chunk), 0x004E4942),
            binary_chunk,
        )
    )
