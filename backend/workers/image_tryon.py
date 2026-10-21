"""Consume image try-on jobs from PostgreSQL and publish validated GLB scenes."""

import hashlib
import json
import logging
import subprocess
import time
from pathlib import Path
from uuid import uuid4

from backend.core.config import Settings
from backend.core.errors import AppException
from backend.db.repository import (
    AssetRepository, BodyRepository, ImageTryOnRepository,
)
from backend.db.session import make_engine, make_session_factory
from backend.schemas.common import AssetSchema, ErrorSchema
from backend.schemas.image_tryon import ImageTryOnResult
from backend.services.blender_body import find_blender_executable
from backend.services.storage import StorageService
from garment.reconstruction.config import get_preset
from garment.reconstruction.contracts import GarmentView, GenerationRequest
from garment.reconstruction.errors import ReconstructionError
from garment.reconstruction.local_pipeline import LocalGarmentReconstructor
from garment.reconstruction.preprocessing import ImagePreprocessor
from garment.reconstruction.validation import GlbValidator

logger = logging.getLogger(__name__)
COMPOSER = Path(__file__).resolve().parents[2] / "garment" / "simulation" / "blender" / "compose_tryon.py"


class ProcessingError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ImageTryOnWorker:
    def __init__(self, settings: Settings, storage: StorageService,
                 jobs: ImageTryOnRepository) -> None:
        self.settings = settings
        self.storage = storage
        self.jobs = jobs

    def run_once(self) -> bool:
        claimed = self.jobs.claim(lease_seconds=900, max_attempts=2)
        if claimed is None:
            return False
        job_id, attempt, request = claimed
        try:
            result = self._process(job_id, request)
            self.jobs.finish(job_id, attempt, result=result.model_dump(mode="json"))
        except (ProcessingError, ReconstructionError, AppException) as exc:
            code = getattr(exc, "code", None) or getattr(getattr(exc, "error", None), "code", "PROCESSING_FAILED")
            message = getattr(exc, "message", None) or str(exc)
            logger.warning("Image try-on job %s failed: %s", job_id, code)
            self.jobs.finish(job_id, attempt, error=ErrorSchema(
                code=code, message=message,
            ).model_dump(mode="json"))
        except Exception:
            logger.exception("Image try-on job %s crashed", job_id)
            self.jobs.finish(job_id, attempt, error=ErrorSchema(
                code="PROCESSING_FAILED", message="Try-on processing failed",
            ).model_dump(mode="json"))
        return True

    def _process(self, job_id: str, request: dict) -> ImageTryOnResult:
        body_id = request["body_id"]
        body_path = self.storage.mpfb_body_path(body_id)
        body_record = self.storage.bodies.get(body_id)
        frame = body_record.metadata_json if body_record else {}
        if any(frame.get(key) != value for key, value in {
            "mesh_unit": "m", "up_axis": "Y", "forward_axis": "+Z",
        }.items()):
            raise ProcessingError("BODY_FRAME_INVALID", "MPFB body frame is not registered")
        root = self.settings.managed_asset_dir.resolve()
        sources = {}
        registered = [asset for asset in self.storage.assets.list(
            kind="original_image", body_id=body_id,
        ) if asset.metadata_json.get("image_tryon_job_id") == job_id]
        for view, key in request["views"].items():
            path = (root / key).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise ProcessingError("SOURCE_IMAGE_MISSING", "Stored garment image is unavailable")
            asset = next((item for item in registered if item.storage_key == key
                          and item.metadata_json.get("view") == view), None)
            if asset is None or asset.byte_size != path.stat().st_size:
                raise ProcessingError("SOURCE_IMAGE_CHANGED", "Stored garment image changed")
            digest = hashlib.sha256()
            with path.open("rb") as image_file:
                for chunk in iter(lambda: image_file.read(1024 * 1024), b""):
                    digest.update(chunk)
            if digest.hexdigest() != asset.sha256:
                raise ProcessingError("SOURCE_IMAGE_CHANGED", "Stored garment image changed")
            sources[GarmentView(view)] = path
        work_dir = root / "image_tryon" / job_id
        preprocessor = ImagePreprocessor(
            max_file_bytes=self.settings.max_garment_image_bytes,
            max_pixels=self.settings.max_garment_image_pixels,
        )
        images = preprocessor.process(sources, work_dir / "normalized")
        generation = GenerationRequest(
            images=images,
            options=get_preset("balanced").to_options(
                seed=0, garment_type=request["garment_type"],
                reference_measurement=request["reference_measurement"],
                reference_value_cm=request["reference_value_cm"],
            ),
        )
        reconstructed = LocalGarmentReconstructor().reconstruct(
            generation, work_dir / "reconstruction",
        )
        metadata = reconstructed.metadata
        if metadata.get("schema_version") != "garment-fit-ready/1.0" or not metadata.get("fit_ready"):
            raise ProcessingError("GARMENT_NOT_FIT_READY", "Garment scale could not be calibrated")
        validator = GlbValidator(max_file_bytes=100 * 1024 * 1024)
        garment_info = validator.validate(reconstructed.model_path)
        output = work_dir / f"scene-{uuid4().hex}.glb"
        report = self._compose(
            body_path, reconstructed.model_path, reconstructed.metadata_path,
            output, bool(request["simulate_cloth"]),
        )
        output_info = validator.validate(output)
        if garment_info.material_count and (
            output_info.material_count == 0 or not output_info.has_pbr_material
        ):
            raise ProcessingError("MATERIAL_LOST", "Combined GLB lost garment materials")
        if garment_info.texture_count and output_info.texture_count == 0:
            raise ProcessingError("TEXTURE_LOST", "Combined GLB lost garment textures")
        name = f"tryon-{job_id}.glb"
        existing = self.storage.assets.get_by_public_name(name)
        if existing is None:
            self.storage.register_asset(
                output, kind="glb", media_type="model/gltf-binary",
                public_name=name, body_id=body_id,
                metadata={"image_tryon_job_id": job_id, "garment_type": request["garment_type"]},
            )
        else:
            self.storage.asset_path(name)
            digest = hashlib.sha256()
            with output.open("rb") as scene_file:
                for chunk in iter(lambda: scene_file.read(1024 * 1024), b""):
                    digest.update(chunk)
            matches = existing.byte_size == output.stat().st_size and existing.sha256 == digest.hexdigest()
            output.unlink(missing_ok=True)
            if not matches:
                raise ProcessingError("ASSET_CONFLICT", "A different scene is already registered for this job")
        asset = AssetSchema(
            source="module", method="blender_static_composition",
            notes=["Contains the selected MPFB body and garment reconstructed from uploaded images."],
            url=f"/api/assets/{name}",
        )
        warnings = list(metadata.get("warnings", []))
        if len(images) == 1:
            warnings.append("BACK_AND_SIDES_INFERRED_FROM_SINGLE_IMAGE")
        return ImageTryOnResult(
            source="module", method="local_parametric_reconstruction_and_blender_placement",
            notes=[
                "Garment scale uses the submitted garment-length reference value.",
                "Garment placement uses a body-height anchor and 1 cm surface clearance.",
                "This scene does not provide a fit score or size recommendation.",
            ],
            body_id=body_id, garment_type=request["garment_type"],
            tryon_mesh=asset, simulation_ran=bool(report["simulation_ran"]),
            penetration_fraction=report["penetration_fraction"],
            placement=report["placement"], warnings=warnings,
            reconstruction={
                "mode": metadata["reconstruction_mode"],
                "segmentation": metadata["segmentation"],
                "scale": metadata["scale"],
                "mesh": metadata["mesh"],
            },
        )

    @staticmethod
    def _compose(body: Path, garment: Path, metadata: Path,
                 output: Path, simulate_cloth: bool) -> dict:
        try:
            blender = find_blender_executable()
        except FileNotFoundError as exc:
            raise ProcessingError("BLENDER_UNAVAILABLE", "Blender executable is unavailable") from exc
        command = [
            blender, "--background", "--python", str(COMPOSER), "--",
            "--body", str(body), "--garment", str(garment),
            "--metadata", str(metadata), "--output", str(output),
        ]
        if simulate_cloth:
            command.append("--simulate-cloth")
        try:
            process = subprocess.run(
                command, capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=240, check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ProcessingError("BLENDER_TIMEOUT", "Blender composition timed out") from exc
        if process.returncode != 0:
            logger.error("Blender composition failed with exit code %s: %s",
                         process.returncode, process.stderr[-2000:])
        elif not output.is_file():
            logger.error("Blender exited successfully but produced no output: %s",
                         process.stderr[-2000:])
        reasons = {
            "SIMULATION_UNAVAILABLE": "Cloth simulation is not calibrated for this garment",
            "GARMENT_FRAME_INVALID": "Garment GLB has an incompatible frame or scale",
            "BODY_MESH_MISSING": "Body GLB contains no mesh",
            "GARMENT_MESH_MISSING": "Garment GLB contains no mesh",
            "BODY_SCALE_INVALID": "Body GLB has an incompatible height",
            "BODY_TORSO_MISSING": "Body GLB has no usable torso cross-section",
            "SEVERE_MESH_PENETRATION": "Garment cannot be aligned to the body safely",
        }
        output_text = process.stdout + process.stderr
        # Always scan for known error codes first — Blender headless may exit
        # with code 0 even when the embedded Python script raises an exception.
        for code, message in reasons.items():
            if code in output_text:
                raise ProcessingError(code, message)
        if process.returncode != 0 or not output.is_file():
            raise ProcessingError("COMPOSITION_FAILED", "Could not compose the body and garment GLB")
        for line in process.stdout.splitlines():
            if line.startswith("TRYON_REPORT="):
                return json.loads(line.partition("=")[2])
        raise ProcessingError("COMPOSITION_REPORT_MISSING", "Blender omitted the quality report")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    engine = make_engine(settings.database_url)
    sessions = make_session_factory(engine)
    storage = StorageService(settings, BodyRepository(sessions), AssetRepository(sessions))
    worker = ImageTryOnWorker(settings, storage, ImageTryOnRepository(sessions))
    try:
        while True:
            try:
                if not worker.run_once():
                    time.sleep(2)
            except Exception:
                logger.exception("Worker loop error; retrying")
                time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Image try-on worker stopped")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
