import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    # Vite dev and the existing Docker frontend mapping, explicitly allowlisted.
    cors_origins: tuple[str, ...] = field(default_factory=lambda: tuple(
        origin.strip() for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,"
            "http://localhost:3000,http://127.0.0.1:3000",
        ).split(",") if origin.strip()
    ))
    asset_dir: Path = Path(__file__).resolve().parents[1] / "fixtures" / "assets"
    max_image_bytes: int = 5 * 1024 * 1024
    max_image_pixels: int = 16_000_000

    def __post_init__(self) -> None:
        if "*" in self.cors_origins:
            raise ValueError("CORS_ORIGINS must list explicit origins")
