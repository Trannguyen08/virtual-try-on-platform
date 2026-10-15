from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .errors import ReconstructionError


class PassthroughPostProcessor:
    name = "passthrough"

    def process(self, source: Path, destination: Path, target_faces: int) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)


class BlenderPostProcessor:
    """Optional Blender headless bridge; never required by the default MVP path."""

    name = "blender"

    def __init__(
        self,
        *,
        executable: str,
        script: Path,
        timeout_seconds: int = 180,
    ) -> None:
        self.executable = executable
        self.script = script
        self.timeout_seconds = timeout_seconds

    def process(self, source: Path, destination: Path, target_faces: int) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        command = [
            self.executable,
            "--background",
            "--factory-startup",
            "--python",
            str(self.script),
            "--",
            str(source),
            str(destination),
            str(target_faces),
        ]
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ReconstructionError(
                "BLENDER_POSTPROCESS_FAILED",
                "Blender post-processing could not be completed",
                retryable=isinstance(exc, subprocess.TimeoutExpired),
                http_status=500,
            ) from exc
        if completed.returncode != 0 or not destination.is_file():
            raise ReconstructionError(
                "BLENDER_POSTPROCESS_FAILED",
                "Blender rejected the generated mesh",
                http_status=500,
            )
