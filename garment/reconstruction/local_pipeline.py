from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
from PIL import Image

from .classifier import auto_detect_garment_type
from .contracts import GarmentView, GenerationRequest, SUPPORTED_GARMENT_TYPES
from .errors import ReconstructionError
from .landmarks import (
    DEFAULT_HEIGHT_METERS,
    build_attachment_regions,
    build_landmark_contract,
    build_measurement_contract,
    calibrate_scale,
    compute_measurements,
    detect_landmarks,
)
from .mesh_builder import GarmentMeshBuilder
from .segmentation import GarmentSegmentor


@dataclass(frozen=True)
class LocalReconstructionResult:
    model_path: Path
    preview_path: Path
    metadata_path: Path
    metadata: dict[str, Any]


class LocalGarmentReconstructor:
    """Build an input-derived, textured garment shell without a cloud service.

    Orchestrates segmentation, landmark detection, parametric mesh construction,
    and PBR texturing across dedicated functional modules.
    """

    def __init__(self, *, grid_resolution: int = 128) -> None:
        if grid_resolution < 24:
            raise ValueError("grid_resolution must be at least 24")
        self.grid_resolution = grid_resolution
        self._segmentor = GarmentSegmentor()
        self._mesh_builder = GarmentMeshBuilder(grid_resolution=grid_resolution)

    def reconstruct(
        self,
        request: GenerationRequest,
        output_dir: Path,
        progress_callback: Callable[[int], None] | None = None,
    ) -> LocalReconstructionResult:
        report = progress_callback or (lambda _progress: None)
        garment_type = request.options.garment_type.lower().strip()
        if garment_type not in SUPPORTED_GARMENT_TYPES:
            raise ReconstructionError(
                "UNSUPPORTED_GARMENT_TYPE",
                f"Unsupported garment type: {garment_type}",
                http_status=422,
            )

        images = request.by_view()
        front_rgb, front_mask, segmentation = self._load_and_segment(
            images[GarmentView.FRONT].path,
            garment_type=garment_type,
        )
        garment_type = segmentation.get("resolved_garment_type", garment_type)
        report(35)

        back_rgb = None
        if GarmentView.BACK in images:
            back_rgb = self._load_rgb(images[GarmentView.BACK].path)

        landmarks = detect_landmarks(front_mask, garment_type)
        measurements_px = compute_measurements(landmarks, garment_type)
        scale = calibrate_scale(
            measurements_px,
            request.options.reference_measurement,
            request.options.reference_value_cm,
            garment_type,
        )
        report(55)

        output_dir.mkdir(parents=True, exist_ok=True)
        model_path = output_dir / "model.glb"
        preview_path = output_dir / "preview.png"
        metadata_path = output_dir / "garment-metadata.json"

        mesh_data = self._mesh_builder.build_mesh(
            front_rgb=front_rgb,
            back_rgb=back_rgb,
            mask=front_mask,
            garment_type=garment_type,
            meters_per_pixel=scale["mesh_meters_per_pixel"],
            landmarks=landmarks,
        )
        report(82)

        model_path.write_bytes(mesh_data["scene"].export(file_type="glb"))
        self._save_preview(front_rgb, front_mask, preview_path)
        report(92)

        warnings = []
        if back_rgb is None:
            warnings.append("BACK_TEXTURE_INFERRED_FROM_FRONT")
        if not scale["calibrated"]:
            warnings.append("ABSOLUTE_SCALE_NOT_CALIBRATED")
        warnings.append("HIDDEN_GEOMETRY_PARAMETRICALLY_INFERRED")
        if segmentation.get("multi_entity_detected"):
            warnings.append("MULTI_ENTITY_SALIENT_GARMENT_ISOLATED")
        if segmentation.get("auto_detected"):
            warnings.append("GARMENT_TYPE_AUTO_DETECTED")
        if segmentation.get("occlusion_inpaint_applied"):
            warnings.append("OCCLUDED_FLANK_SYMMETRICALLY_RECOVERED")

        metadata = {
            "schema_version": "garment-fit-ready/1.0",
            "reconstruction_mode": "local_parametric",
            "fit_ready": bool(scale["calibrated"]),
            "garment_type": garment_type,
            "auto_detected": bool(segmentation.get("auto_detected", False)),
            "coordinate_system": {
                "handedness": "right",
                "up_axis": "Y",
                "forward_axis": "+Z",
                "mesh_unit": "m",
                "measurement_unit": "cm",
            },
            "scale": {
                "calibrated": scale["calibrated"],
                "cm_per_pixel": scale["cm_per_pixel"],
                "calibrated_from": scale["calibrated_from"],
                "mesh_scale_source": scale["mesh_scale_source"],
                "confidence": scale["confidence"],
            },
            "segmentation": segmentation,
            "measurements": build_measurement_contract(
                measurements_px,
                scale["cm_per_pixel"],
                request.options.reference_measurement,
            ),
            "landmarks": build_landmark_contract(
                landmarks,
                mesh_data["landmark_vertices"],
                front_mask,
            ),
            "openings": mesh_data["openings"],
            "attachment_regions": build_attachment_regions(
                garment_type, mesh_data["landmark_vertices"]
            ),
            "mesh": {
                "front_node": "GarmentFront",
                "back_node": "GarmentBack",
                "seams_node": "GarmentSeams" if "GarmentSeams" in mesh_data["scene"].geometry else None,
                "front_vertices": mesh_data["front_vertex_count"],
                "back_vertices": mesh_data["back_vertex_count"],
                "total_triangles": mesh_data["triangle_count"],
                "grid_resolution": self.grid_resolution,
            },
            "warnings": warnings,
        }
        metadata_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        report(100)
        return LocalReconstructionResult(
            model_path=model_path,
            preview_path=preview_path,
            metadata_path=metadata_path,
            metadata=metadata,
        )

    def _load_and_segment(
        self, path: Path, garment_type: str = "auto"
    ) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
        return self._segmentor.load_and_segment(path, garment_type=garment_type)

    @classmethod
    def _clean_mask(cls, mask: np.ndarray) -> np.ndarray:
        cleaned, _ = GarmentSegmentor.isolate_and_clean_salient_garment(mask)
        return cleaned

    @staticmethod
    def _load_rgb(path: Path) -> np.ndarray:
        with Image.open(path) as source:
            return np.asarray(source.convert("RGB"), dtype=np.uint8)

    @staticmethod
    def _save_preview(rgb: np.ndarray, mask: np.ndarray, destination: Path) -> None:
        rgba = np.dstack((rgb, (mask.astype(np.uint8) * 255)))
        Image.fromarray(rgba, mode="RGBA").save(destination, format="PNG")
