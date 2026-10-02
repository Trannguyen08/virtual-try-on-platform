from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
ROOT_ENV_FILE = WORKSPACE_ROOT / ".env"


def _integer(name: str, default: int) -> int:
    raw = os.getenv(name)
    return int(raw) if raw else default


@dataclass(frozen=True)
class Garment3DSettings:
    provider: str
    preset: str
    output_dir: Path
    sqlite_path: Path
    tripo_api_key: str
    tripo_base_url: str
    tripo_model: str
    postprocessor: str
    blender_executable: str
    blender_script: Path
    max_upload_bytes: int
    max_artifact_bytes: int
    poll_cache_seconds: int

    @classmethod
    def from_environment(cls) -> Garment3DSettings:
        # This standalone local module uses the ignored root .env as its source
        # of truth, preventing stale PowerShell variables from shadowing a key
        # that the developer has just updated there.
        load_dotenv(dotenv_path=ROOT_ENV_FILE, override=True)
        data_dir = Path(
            os.getenv("GARMENT3D_DATA_DIR", str(WORKSPACE_ROOT / "data"))
        ).resolve()
        return cls(
            provider=os.getenv("GARMENT3D_PROVIDER", "mock").lower(),
            preset=os.getenv("GARMENT3D_PRESET", "balanced").lower(),
            output_dir=Path(
                os.getenv(
                    "GARMENT3D_OUTPUT_DIR", str(data_dir / "outputs" / "garment_3d")
                )
            ).resolve(),
            sqlite_path=Path(
                os.getenv("GARMENT3D_SQLITE_PATH", str(data_dir / "garment3d.sqlite3"))
            ).resolve(),
            tripo_api_key=os.getenv("TRIPO_API_KEY", ""),
            tripo_base_url=os.getenv("TRIPO_BASE_URL", "https://openapi.tripo3d.ai/v3"),
            tripo_model=os.getenv("GARMENT3D_MODEL_REVISION", "v3.1-20260211"),
            postprocessor=os.getenv("GARMENT3D_POSTPROCESSOR", "passthrough").lower(),
            blender_executable=os.getenv("BLENDER_EXECUTABLE", "blender"),
            blender_script=Path(
                os.getenv(
                    "GARMENT3D_BLENDER_SCRIPT",
                    str(WORKSPACE_ROOT / "scripts" / "blender" / "process_garment.py"),
                )
            ).resolve(),
            max_upload_bytes=_integer("GARMENT3D_MAX_UPLOAD_BYTES", 10 * 1024 * 1024),
            max_artifact_bytes=_integer(
                "GARMENT3D_MAX_ARTIFACT_BYTES", 50 * 1024 * 1024
            ),
            poll_cache_seconds=_integer("GARMENT3D_POLL_CACHE_SECONDS", 3),
        )

    def validate(self) -> None:
        if self.provider not in {"mock", "tripo"}:
            raise ValueError("GARMENT3D_PROVIDER must be 'mock' or 'tripo'")
        if self.provider == "tripo" and not self.tripo_api_key:
            raise ValueError("TRIPO_API_KEY is required for GARMENT3D_PROVIDER=tripo")
        if self.postprocessor not in {"passthrough", "blender"}:
            raise ValueError(
                "GARMENT3D_POSTPROCESSOR must be 'passthrough' or 'blender'"
            )
