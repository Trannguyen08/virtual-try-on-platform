from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Protocol


class GarmentView(str, Enum):
    FRONT = "front"
    LEFT = "left"
    BACK = "back"
    RIGHT = "right"


VIEW_ORDER = (
    GarmentView.FRONT,
    GarmentView.LEFT,
    GarmentView.BACK,
    GarmentView.RIGHT,
)


class TaskState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class GarmentImage:
    view: GarmentView
    path: Path
    sha256: str
    media_type: str
    width: int
    height: int
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class GenerationOptions:
    preset: str = "balanced"
    target_face_count: int = 30_000
    generate_texture: bool = True
    generate_pbr: bool = True
    seed: int = 0


@dataclass(frozen=True)
class GenerationRequest:
    images: tuple[GarmentImage, ...]
    options: GenerationOptions = field(default_factory=GenerationOptions)

    def __post_init__(self) -> None:
        views = [image.view for image in self.images]
        if not images_are_valid(self.images):
            raise ValueError("Generation requires 1-4 unique views including front")
        if len(views) != len(set(views)):
            raise ValueError("Each garment view may only be provided once")

    @property
    def is_multi_view(self) -> bool:
        return len(self.images) > 1

    def by_view(self) -> Mapping[GarmentView, GarmentImage]:
        return {image.view: image for image in self.images}


def images_are_valid(images: Sequence[GarmentImage]) -> bool:
    if not 1 <= len(images) <= 4:
        return False
    views = [image.view for image in images]
    return GarmentView.FRONT in views and len(views) == len(set(views))


@dataclass(frozen=True)
class ProviderTask:
    provider: str
    external_id: str


@dataclass(frozen=True)
class ProviderResult:
    model_url: str
    thumbnail_url: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderTaskStatus:
    state: TaskState
    progress: int
    result: ProviderResult | None = None
    error_code: str | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class MeshMetadata:
    file_size_bytes: int
    mesh_count: int
    primitive_count: int
    triangle_count: int | None
    material_count: int
    texture_count: int
    has_pbr_material: bool


class Garment3DProvider(Protocol):
    name: str

    async def create_task(self, request: GenerationRequest) -> ProviderTask: ...

    async def get_task(self, external_id: str) -> ProviderTaskStatus: ...

    async def download(self, url: str, destination: Path, max_bytes: int) -> None: ...

    async def cancel_task(self, external_id: str) -> bool: ...

    async def close(self) -> None: ...


class MeshPostProcessor(Protocol):
    name: str

    def process(self, source: Path, destination: Path, target_faces: int) -> None: ...
