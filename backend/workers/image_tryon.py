"""Consume image try-on jobs from PostgreSQL and publish validated GLB scenes."""

import hashlib
import json
import logging
import os
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
from backend.schemas.image_tryon import ImageTryOnGarmentResult, ImageTryOnResult
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
        started = time.perf_counter()
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
        finally:
            logger.info("Image try-on job %s attempt %s finished in %.2fs",
                        job_id, attempt, time.perf_counter() - started)
        return True

    def _process(self, job_id: str, request: dict) -> ImageTryOnResult:
        stage_started = time.perf_counter()
        body_id = request["body_id"]
        body_path = self.storage.mpfb_body_path(body_id)
        body_record = self.storage.bodies.get(body_id)
        frame = body_record.metadata_json if body_record else {}
        body_parameters = frame.get("parameters") or {}
        body_measurements = body_parameters.get("measurements_cm") or {}
        if any(frame.get(key) != value for key, value in {
            "mesh_unit": "m", "up_axis": "Y", "forward_axis": "+Z",
        }.items()):
            raise ProcessingError("BODY_FRAME_INVALID", "MPFB body frame is not registered")
        root = self.settings.managed_asset_dir.resolve()
        registered = [asset for asset in self.storage.assets.list(
            kind="original_image", body_id=body_id,
        ) if asset.metadata_json.get("image_tryon_job_id") == job_id]
        work_dir = root / "image_tryon" / job_id
        garment_requests = request.get("garments")
        if not garment_requests:
            # Read jobs created before the outfit contract was introduced.
            garment_type = request["garment_type"]
            slot = ("upper" if garment_type in {"tshirt", "shirt", "jacket"}
                    else "onepiece" if garment_type == "dress" else "lower")
            garment_requests = [{
                "slot": slot, "garment_type": garment_type,
                "reference_measurement": request.get("reference_measurement", "garment_length"),
                "reference_value_cm": request.get("reference_value_cm", 70),
                "views": request.get("views", {}),
            }]
        reconstructed_items = []
        for index, garment_request in enumerate(garment_requests):
            source_views = garment_request.get("views") or request.get("views", {})
            sources = {}
            for view, key in source_views.items():
                path = (root / key).resolve()
                if not path.is_relative_to(root) or not path.is_file():
                    raise ProcessingError("SOURCE_IMAGE_MISSING", "Stored garment image is unavailable")
                asset_view = f"{index}_{view}" if garment_request.get("views") else view
                asset = next((item for item in registered if item.storage_key == key
                              and item.metadata_json.get("view") == asset_view), None)
                if asset is None or asset.byte_size != path.stat().st_size:
                    raise ProcessingError("SOURCE_IMAGE_CHANGED", "Stored garment image changed")
                digest = hashlib.sha256()
                with path.open("rb") as image_file:
                    for chunk in iter(lambda: image_file.read(1024 * 1024), b""):
                        digest.update(chunk)
                if digest.hexdigest() != asset.sha256:
                    raise ProcessingError("SOURCE_IMAGE_CHANGED", "Stored garment image changed")
                sources[GarmentView(view)] = path
            preprocessor = ImagePreprocessor(
                max_file_bytes=self.settings.max_garment_image_bytes,
                max_pixels=self.settings.max_garment_image_pixels,
            )
            images = preprocessor.process(sources, work_dir / f"garment_{index}" / "normalized")
            fit_mode = garment_request.get("fit_mode", "auto")
            garment_measurements = garment_request.get("garment_measurements_cm") or {}
            if fit_mode == "measurements":
                if garment_request["slot"] in {"upper", "onepiece"}:
                    reference_measurement = "chest_circumference_est"
                    reference_value_cm = garment_measurements["chest_circumference_cm"]
                else:
                    reference_measurement = "waist_circumference_est"
                    reference_value_cm = garment_measurements["waist_circumference_cm"]
            else:
                reference_measurement = garment_request["reference_measurement"]
                reference_value_cm = garment_request["reference_value_cm"]
            generation = GenerationRequest(
                images=images,
                options=get_preset("balanced").to_options(
                    seed=0, garment_type=garment_request["garment_type"],
                    reference_measurement=reference_measurement,
                    reference_value_cm=reference_value_cm,
                ),
            )
            reconstructed = LocalGarmentReconstructor().reconstruct(
                generation, work_dir / f"garment_{index}" / "reconstruction",
            )
            metadata = reconstructed.metadata
            if metadata.get("schema_version") != "garment-fit-ready/1.0" or not metadata.get("fit_ready"):
                raise ProcessingError("GARMENT_NOT_FIT_READY", "Garment scale could not be calibrated")
            composition_metadata_path = work_dir / f"garment_{index}" / "composition-metadata.json"
            composition_metadata = dict(metadata)
            composition_metadata["body_measurements_cm"] = body_measurements
            composition_metadata["fit_settings"] = {
                "mode": fit_mode,
                "ease_cm": garment_request.get("ease_cm", 4),
                "garment_measurements_cm": garment_measurements,
            }
            composition_metadata_path.write_text(
                json.dumps(composition_metadata, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            reconstructed_items.append({
                "request": garment_request, "images": images,
                "reconstructed": reconstructed,
                "composition_metadata_path": composition_metadata_path,
            })
        logger.info("Image try-on job %s reconstructed %s garment(s) in %.2fs",
                    job_id, len(reconstructed_items), time.perf_counter() - stage_started)
        validator = GlbValidator(max_file_bytes=100 * 1024 * 1024)
        garment_infos = [validator.validate(item["reconstructed"].model_path)
                         for item in reconstructed_items]
        output = work_dir / f"scene-{uuid4().hex}.glb"
        stage_started = time.perf_counter()
        logger.info("Image try-on job %s starting Blender composition", job_id)
        report = self._compose(
            body_path,
            [item["reconstructed"].model_path for item in reconstructed_items],
            [item["composition_metadata_path"] for item in reconstructed_items],
            output, bool(request["simulate_cloth"]),
        )
        logger.info("Image try-on job %s Blender composition: %.2fs",
                    job_id, time.perf_counter() - stage_started)
        output_info = validator.validate(output)
        if any(info.material_count for info in garment_infos) and (
            output_info.material_count == 0 or not output_info.has_pbr_material
        ):
            raise ProcessingError("MATERIAL_LOST", "Combined GLB lost garment materials")
        if any(info.texture_count for info in garment_infos) and output_info.texture_count == 0:
            raise ProcessingError("TEXTURE_LOST", "Combined GLB lost garment textures")
        name = f"tryon-{job_id}.glb"
        existing = self.storage.assets.get_by_public_name(name)
        if existing is None:
            published_path = root / name
            temporary_path = root / f".{name}.{uuid4().hex}.part"
            os.replace(output, temporary_path)
            os.replace(temporary_path, published_path)
            self.storage.register_asset(
                published_path, kind="glb", media_type="model/gltf-binary",
                public_name=name, body_id=body_id,
                metadata={
                    "image_tryon_job_id": job_id,
                    "garment_types": [item["request"]["garment_type"] for item in reconstructed_items],
                },
            )
        else:
            digest = hashlib.sha256()
            with output.open("rb") as scene_file:
                for chunk in iter(lambda: scene_file.read(1024 * 1024), b""):
                    digest.update(chunk)
            matches = existing.byte_size == output.stat().st_size and existing.sha256 == digest.hexdigest()
            try:
                self.storage.asset_path(name)
                asset_is_available = True
            except AppException:
                asset_is_available = False
            if asset_is_available:
                output.unlink(missing_ok=True)
                if not matches:
                    raise ProcessingError("ASSET_CONFLICT", "A different scene is already registered for this job")
            else:
                published_path = root / name
                temporary_path = root / f".{name}.{uuid4().hex}.part"
                os.replace(output, temporary_path)
                os.replace(temporary_path, published_path)
                if not self.storage.assets.restore_managed_glb(
                    existing.asset_id, key=name,
                    byte_size=published_path.stat().st_size,
                    sha256=digest.hexdigest(),
                ):
                    raise ProcessingError("ASSET_REGISTRATION_FAILED", "Could not restore the try-on scene asset")
        asset = AssetSchema(
            source="module", method="blender_static_composition",
            notes=["Contains the selected MPFB body and garment reconstructed from uploaded images."],
            url=f"/api/assets/{name}",
        )
        garment_results = []
        warnings = []
        reconstruction_results = []
        for item in reconstructed_items:
            garment_request = item["request"]
            metadata = item["reconstructed"].metadata
            garment_reconstruction = {
                "mode": metadata["reconstruction_mode"],
                "segmentation": metadata["segmentation"],
                "scale": metadata["scale"],
                "mesh": metadata["mesh"],
                "fit": {
                    "mode": garment_request.get("fit_mode", "auto"),
                    "ease_cm": garment_request.get("ease_cm", 4),
                    "garment_measurements_cm": garment_request.get("garment_measurements_cm"),
                },
            }
            garment_results.append(ImageTryOnGarmentResult(
                slot=garment_request["slot"],
                garment_type=garment_request["garment_type"],
                reconstruction=garment_reconstruction,
            ))
            reconstruction_results.append({
                "slot": garment_request["slot"],
                "garment_type": garment_request["garment_type"],
                **garment_reconstruction,
            })
            warnings.extend(metadata.get("warnings", []))
            if len(item["images"]) == 1:
                warnings.append(f"{garment_request['slot'].upper()}_BACK_INFERRED_FROM_FRONT")
        return ImageTryOnResult(
            source="module", method="local_parametric_reconstruction_and_blender_placement",
            notes=[
                "Garment width follows body measurements plus ease, or user-entered garment circumferences.",
                "Garment placement is a static shell with 1 cm body clearance; cloth simulation is unavailable.",
                "This scene does not provide a fit score or size recommendation.",
            ],
            body_id=body_id,
            garment_type=(reconstructed_items[0]["request"]["garment_type"]
                          if len(reconstructed_items) == 1 else "outfit"),
            garments=garment_results,
            tryon_mesh=asset, simulation_ran=bool(report["simulation_ran"]),
            penetration_fraction=report["penetration_fraction"],
            placement=report["placement"], warnings=warnings,
            reconstruction={"garments": reconstruction_results},
        )

    @staticmethod
    def _compose(body: Path, garments: list[Path], metadata: list[Path],
                 output: Path, simulate_cloth: bool) -> dict:
        try:
            blender = find_blender_executable()
        except FileNotFoundError as exc:
            raise ProcessingError("BLENDER_UNAVAILABLE", "Blender executable is unavailable") from exc
        command = [
            blender, "--background", "--factory-startup", "--python-exit-code", "1",
            "--python", str(COMPOSER), "--",
            "--body", str(body), "--output", str(output),
        ]
        for garment, garment_metadata in zip(garments, metadata, strict=True):
            command.extend(["--garment", str(garment), "--metadata", str(garment_metadata)])
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
            "BODY_MEASUREMENTS_MISSING": "Save body measurements or enter garment measurements manually",
            "GARMENT_MEASUREMENT_MISMATCH": "Garment dimensions require an unsafe width adjustment",
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
