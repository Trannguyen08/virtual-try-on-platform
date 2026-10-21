"""Isolated Blender jobs for manually configured body meshes.

These meshes are visualizations. They do not produce measured dimensions or fit scores.
"""

import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from threading import RLock
from uuid import uuid4

from backend.core.errors import AppException
from backend.services.storage import StorageService
from garment.reconstruction.validation import GlbValidator

logger = logging.getLogger(__name__)
SCRIPT = Path(__file__).resolve().parents[2] / "body" / "estimation" / "blender_body.py"
OUTPUT = Path(__file__).resolve().parents[2] / "data" / "outputs" / "blender_body"


def find_blender_executable() -> str:
    """Resolve Blender from explicit configuration, PATH, then common Windows installs."""
    configured = os.getenv("BLENDER_PATH", "").strip().strip('"')
    if configured:
        if Path(configured).is_file():
            return configured
        executable = shutil.which(configured)
        if executable:
            return executable
        raise FileNotFoundError("Configured BLENDER_PATH is unavailable")

    executable = shutil.which("blender")
    if executable:
        return executable

    if os.name == "nt":
        for drive in ("C", "D", "E"):
            candidate = Path(f"{drive}:/Blender/blender.exe")
            if candidate.is_file():
                return str(candidate)
        program_files = os.getenv("ProgramFiles", "C:/Program Files")
        install_root = Path(program_files) / "Blender Foundation"
        for candidate in sorted(install_root.glob("Blender */blender.exe"), reverse=True):
            if candidate.is_file():
                return str(candidate)

    raise FileNotFoundError("Blender executable is unavailable")


class BlenderBodyJobs:
    def __init__(self, storage: StorageService | None = None) -> None:
        self._jobs: dict[str, dict] = {}
        self._lock = RLock()
        self.storage = storage

    def create(self, action: str, parameters: dict, source_id: str | None = None) -> dict:
        if source_id is not None:
            source = self.get(source_id)
            if source["status"] != "completed" or source["action"] != "body":
                raise AppException(422, "BODY_NOT_READY", "Generate a body before adding clothing")
        job_id = uuid4().hex
        job = {"job_id": job_id, "body_id": job_id if action == "body" else None,
               "action": action, "status": "pending",
               "source_id": source_id, "asset_url": None, "error": None,
               "method": None, "source": "mock"}
        with self._lock:
            if sum(item["status"] in {"pending", "running"} for item in self._jobs.values()) >= 2:
                raise AppException(429, "BLENDER_BUSY", "Blender is busy; try again shortly")
            self._jobs[job_id] = job
        return job.copy()

    def get(self, job_id: str) -> dict:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                raise AppException(404, "JOB_NOT_FOUND", "Blender job not found")
            return job.copy()

    def asset(self, job_id: str) -> Path:
        job = self.get(job_id)
        if job["status"] != "completed":
            raise AppException(404, "ASSET_NOT_FOUND", "Generated model is not ready")
        path = OUTPUT / f"{job_id}.glb"
        if not path.is_file():
            raise AppException(404, "ASSET_NOT_FOUND", "Generated model is unavailable")
        return path

    def run(self, job_id: str, parameters: dict) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job["status"] = "running"
        try:
            blender = find_blender_executable()
            OUTPUT.mkdir(parents=True, exist_ok=True)
            output = OUTPUT / f"{job_id}.glb"
            source_id = job["source_id"]
            command = [blender, "--background", "--python", str(SCRIPT), "--",
                       "--action", job["action"], "--output", str(output),
                       "--params", json.dumps(parameters)]
            if source_id:
                command += ["--source", str(self.asset(source_id))]
            result = subprocess.run(command, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace",
                                    timeout=180, check=False)
            if result.returncode != 0 or not output.is_file() or output.stat().st_size < 100:
                logger.error("Blender %s failed (exit %s, MPFB unavailable: %s)",
                             job["action"], result.returncode,
                             "MPFB_UNAVAILABLE" in result.stderr or
                             "MPFB_UNAVAILABLE" in result.stdout)
                raise RuntimeError("BLENDER_FAILED")
            if job["action"] == "body" and "BODY_METHOD=mpfb" not in result.stdout:
                raise RuntimeError("MPFB_RESULT_MISSING")
            if job["action"] == "body" and self.storage is not None:
                GlbValidator(max_file_bytes=100 * 1024 * 1024).validate(output)
                body_dir = self.storage.settings.managed_asset_dir / "bodies"
                body_dir.mkdir(parents=True, exist_ok=True)
                managed = body_dir / f"{job_id}.glb"
                temporary = body_dir / f"{job_id}.glb.part"
                try:
                    shutil.copyfile(output, temporary)
                    os.replace(temporary, managed)
                    self.storage.register_mpfb_body(job_id, managed, metadata={
                        "mesh_unit": "m", "up_axis": "Y", "forward_axis": "+Z",
                        "pose": "mpfb_export", "height_cm": parameters["height_cm"],
                    })
                finally:
                    temporary.unlink(missing_ok=True)
            method = ("blender_asset_clothing" if job["action"] == "clothing" and "CLOTHING_METHOD=asset" in result.stdout
                      else "blender_illustrative_clothing" if job["action"] == "clothing"
                      else "blender_mpfb")
            source = ("mixed" if method == "blender_asset_clothing" and
                      self.get(source_id)["source"] == "mock" else
                      "module" if method in {"blender_mpfb", "blender_asset_clothing"} else "mock")
            with self._lock:
                asset_url = (f"/api/assets/body-{job_id}.glb"
                             if job["action"] == "body" and self.storage is not None
                             else f"/api/body-builder/assets/{job_id}.glb")
                job.update(status="completed", asset_url=asset_url,
                           method=method, source=source)
        except FileNotFoundError:
            logger.warning("Blender executable was not found for job %s", job_id)
            with self._lock:
                job.update(status="failed", error=(
                    "Backend không tìm thấy blender.exe. Kiểm tra BLENDER_PATH hoặc vị trí cài Blender."
                ))
        except Exception:
            logger.exception("Blender body job %s failed", job_id)
            with self._lock:
                job.update(status="failed", error=(
                    "Không thể tạo body MPFB. Kiểm tra add-on MPFB2 trong Blender và log backend."
                    if job["action"] == "body" else
                    "Không thể tạo trang phục trong Blender. Kiểm tra log backend."
                ))

