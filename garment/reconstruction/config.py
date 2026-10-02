from __future__ import annotations

from dataclasses import dataclass

from .contracts import GenerationOptions


@dataclass(frozen=True)
class GenerationPreset:
    name: str
    target_face_count: int
    generate_texture: bool
    generate_pbr: bool

    def to_options(self, *, seed: int = 0) -> GenerationOptions:
        return GenerationOptions(
            preset=self.name,
            target_face_count=self.target_face_count,
            generate_texture=self.generate_texture,
            generate_pbr=self.generate_pbr,
            seed=seed,
        )


PRESETS = {
    "preview": GenerationPreset("preview", 20_000, True, False),
    "balanced": GenerationPreset("balanced", 30_000, True, True),
    "quality": GenerationPreset("quality", 80_000, True, True),
}


def get_preset(name: str) -> GenerationPreset:
    try:
        return PRESETS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown garment 3D preset: {name}") from exc
