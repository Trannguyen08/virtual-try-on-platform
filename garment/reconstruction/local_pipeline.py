from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import cv2
import numpy as np
import trimesh
from PIL import Image

from .contracts import GarmentView, GenerationRequest, SUPPORTED_GARMENT_TYPES
from .errors import ReconstructionError

DEFAULT_HEIGHT_METERS = {
    "tshirt": 0.68,
    "shirt": 0.72,
    "jacket": 0.74,
    "pants": 1.02,
    "skirt": 0.65,
    "dress": 1.10,
}


@dataclass(frozen=True)
class LocalReconstructionResult:
    model_path: Path
    preview_path: Path
    metadata_path: Path
    metadata: dict[str, Any]


class LocalGarmentReconstructor:
    """Build an input-derived, textured garment shell without a cloud service.

    The output is a parametric reconstruction, not a claim that hidden geometry was
    recovered from a single photograph. Front/back panels are curved into 3D and
    joined at detected silhouette boundaries while garment openings stay open.
    """

    def __init__(self, *, grid_resolution: int = 128) -> None:
        if grid_resolution < 24:
            raise ValueError("grid_resolution must be at least 24")
        self.grid_resolution = grid_resolution

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
            images[GarmentView.FRONT].path
        )
        report(35)
        back_rgb = None
        if GarmentView.BACK in images:
            back_rgb = self._load_rgb(images[GarmentView.BACK].path)

        landmarks = self._detect_landmarks(front_mask, garment_type)
        measurements_px = self._measurements(landmarks, garment_type)
        scale = self._calibrate_scale(
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

        mesh_data = self._build_mesh(
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

        metadata = {
            "schema_version": "garment-fit-ready/1.0",
            "reconstruction_mode": "local_parametric",
            "fit_ready": bool(scale["calibrated"]),
            "garment_type": garment_type,
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
            "measurements": self._measurement_contract(
                measurements_px,
                scale["cm_per_pixel"],
                request.options.reference_measurement,
            ),
            "landmarks": self._landmark_contract(
                landmarks,
                mesh_data["landmark_vertices"],
                front_mask,
            ),
            "openings": mesh_data["openings"],
            "attachment_regions": self._attachment_regions(
                garment_type, mesh_data["landmark_vertices"]
            ),
            "mesh": {
                "front_node": "GarmentFront",
                "back_node": "GarmentBack",
                "seam_node": "GarmentSeams",
                "front_vertex_count": mesh_data["front_vertex_count"],
                "back_vertex_count": mesh_data["back_vertex_count"],
                "triangle_count": mesh_data["triangle_count"],
                "is_parametric_reconstruction": True,
            },
            "warnings": warnings,
        }
        metadata_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return LocalReconstructionResult(
            model_path=model_path,
            preview_path=preview_path,
            metadata_path=metadata_path,
            metadata=metadata,
        )

    @staticmethod
    def _load_rgb(path: Path) -> np.ndarray:
        with Image.open(path) as source:
            return np.asarray(source.convert("RGB"), dtype=np.uint8)

    def _load_and_segment(
        self, path: Path
    ) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
        with Image.open(path) as source:
            rgba = np.asarray(source.convert("RGBA"), dtype=np.uint8)
        rgb = rgba[:, :, :3]
        alpha = rgba[:, :, 3]
        transparent_ratio = float(np.mean(alpha < 245))

        if transparent_ratio >= 0.01:
            mask = alpha >= 16
            method = "input_alpha"
        else:
            mask = self._background_difference_mask(rgb)
            method = "opencv_border_color"
            if not self._coverage_is_valid(mask):
                mask = self._grabcut_mask(rgb)
                method = "opencv_grabcut"

        mask = self._clean_mask(mask)
        if not self._coverage_is_valid(mask):
            raise ReconstructionError(
                "GARMENT_MASK_NOT_DETECTED",
                "Could not isolate a garment. Use a plain contrasting background or a PNG with transparency.",
                http_status=422,
            )

        border_pixels = np.concatenate(
            (mask[0, :], mask[-1, :], mask[:, 0], mask[:, -1])
        )
        border_leak = float(np.mean(border_pixels))
        coverage = float(np.mean(mask))
        confidence = max(0.35, min(0.98, 0.94 - border_leak * 1.8))
        return rgb, mask, {
            "method": method,
            "coverage_ratio": round(coverage, 4),
            "border_leak_ratio": round(border_leak, 4),
            "confidence": round(confidence, 3),
        }

    @staticmethod
    def _background_difference_mask(rgb: np.ndarray) -> np.ndarray:
        height, width = rgb.shape[:2]
        band = max(2, min(height, width) // 40)
        border = np.concatenate(
            (
                rgb[:band].reshape(-1, 3),
                rgb[-band:].reshape(-1, 3),
                rgb[:, :band].reshape(-1, 3),
                rgb[:, -band:].reshape(-1, 3),
            )
        ).astype(np.float32)
        background = np.median(border, axis=0)
        distance = np.linalg.norm(rgb.astype(np.float32) - background, axis=2)
        border_distance = np.linalg.norm(border - background, axis=1)
        threshold = max(22.0, float(np.percentile(border_distance, 97)) + 12.0)
        return distance > threshold

    @staticmethod
    def _grabcut_mask(rgb: np.ndarray) -> np.ndarray:
        height, width = rgb.shape[:2]
        inset_x = max(2, int(width * 0.03))
        inset_y = max(2, int(height * 0.03))
        state = np.zeros((height, width), dtype=np.uint8)
        background_model = np.zeros((1, 65), dtype=np.float64)
        foreground_model = np.zeros((1, 65), dtype=np.float64)
        rectangle = (
            inset_x,
            inset_y,
            max(1, width - 2 * inset_x),
            max(1, height - 2 * inset_y),
        )
        cv2.grabCut(
            cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR),
            state,
            rectangle,
            background_model,
            foreground_model,
            5,
            cv2.GC_INIT_WITH_RECT,
        )
        return np.logical_or(state == cv2.GC_FGD, state == cv2.GC_PR_FGD)

    @staticmethod
    def _clean_mask(mask: np.ndarray) -> np.ndarray:
        binary = mask.astype(np.uint8) * 255
        kernel = np.ones((5, 5), dtype=np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
        count, labels, stats, _ = cv2.connectedComponentsWithStats(binary, 8)
        if count <= 1:
            return np.zeros_like(mask, dtype=bool)
        largest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        component = (labels == largest).astype(np.uint8) * 255
        contours, _ = cv2.findContours(
            component, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if contours:
            cv2.drawContours(component, contours, -1, 255, thickness=cv2.FILLED)
        return component > 0

    @staticmethod
    def _coverage_is_valid(mask: np.ndarray) -> bool:
        coverage = float(np.mean(mask))
        return 0.025 <= coverage <= 0.92

    def _detect_landmarks(
        self, mask: np.ndarray, garment_type: str
    ) -> dict[str, tuple[float, float]]:
        ys, xs = np.nonzero(mask)
        if not len(xs):
            raise ReconstructionError(
                "GARMENT_MASK_EMPTY", "Garment mask contains no foreground pixels"
            )
        left, right = float(xs.min()), float(xs.max())
        top, bottom = float(ys.min()), float(ys.max())
        width = max(1.0, right - left)
        height = max(1.0, bottom - top)
        center_x = (left + right) / 2.0

        def row(fraction: float) -> tuple[tuple[float, float], tuple[float, float]]:
            target = int(round(top + fraction * height))
            for offset in range(0, max(3, int(height * 0.05))):
                for candidate in (target + offset, target - offset):
                    if 0 <= candidate < mask.shape[0]:
                        row_x = np.flatnonzero(mask[candidate])
                        if len(row_x) >= 2:
                            return (
                                (float(row_x.min()), float(candidate)),
                                (float(row_x.max()), float(candidate)),
                            )
            return (left, float(target)), (right, float(target))

        if garment_type == "pants":
            waist_left, waist_right = row(0.04)
            hip_left, hip_right = row(0.20)
            crotch_left, crotch_right = row(0.43)
            crotch_center = (
                (crotch_left[0] + crotch_right[0]) / 2.0,
                crotch_left[1],
            )
            return {
                "waist_left": waist_left,
                "waist_right": waist_right,
                "hip_left": hip_left,
                "hip_right": hip_right,
                "crotch_center": crotch_center,
                "left_hem": (left + width * 0.22, bottom),
                "right_hem": (right - width * 0.22, bottom),
                "garment_top": (center_x, top),
                "garment_bottom": (center_x, bottom),
            }

        if garment_type == "skirt":
            waist_left, waist_right = row(0.04)
            hip_left, hip_right = row(0.28)
            hem_left, hem_right = row(0.96)
            return {
                "waist_left": waist_left,
                "waist_right": waist_right,
                "hip_left": hip_left,
                "hip_right": hip_right,
                "hem_left": hem_left,
                "hem_right": hem_right,
                "garment_top": (center_x, top),
                "garment_bottom": (center_x, bottom),
            }

        waist_left, waist_right = row(0.70)
        hem_left, hem_right = row(0.96)
        torso_width = max(
            waist_right[0] - waist_left[0],
            hem_right[0] - hem_left[0],
        )
        shoulder_half = torso_width * 0.37
        chest_half = torso_width * 0.50
        shoulder_y = top + height * 0.14
        chest_y = top + height * 0.38
        shoulder_left = (center_x - shoulder_half, shoulder_y)
        shoulder_right = (center_x + shoulder_half, shoulder_y)
        chest_left = (center_x - chest_half, chest_y)
        chest_right = (center_x + chest_half, chest_y)
        neck_half = min(width * 0.11, torso_width * 0.20)
        neck_center_y = top + height * 0.038
        points = np.column_stack((xs, ys))
        upper = points[points[:, 1] <= top + height * 0.48]
        sleeve_left = tuple(map(float, upper[np.argmin(upper[:, 0])]))
        sleeve_right = tuple(map(float, upper[np.argmax(upper[:, 0])]))
        return {
            "neck_center": (center_x, neck_center_y),
            "neck_left": (center_x - neck_half, top + height * 0.015),
            "neck_right": (center_x + neck_half, top + height * 0.015),
            "left_shoulder": shoulder_left,
            "right_shoulder": shoulder_right,
            "left_armpit": chest_left,
            "right_armpit": chest_right,
            "left_sleeve_end": sleeve_left,
            "right_sleeve_end": sleeve_right,
            "waist_left": waist_left,
            "waist_right": waist_right,
            "hem_left": hem_left,
            "hem_right": hem_right,
            "garment_top": (center_x, top),
            "garment_bottom": (center_x, bottom),
        }

    @staticmethod
    def _distance(
        first: tuple[float, float], second: tuple[float, float]
    ) -> float:
        return math.dist(first, second)

    def _measurements(
        self,
        landmarks: dict[str, tuple[float, float]],
        garment_type: str,
    ) -> dict[str, tuple[float, str, float]]:
        length = self._distance(landmarks["garment_top"], landmarks["garment_bottom"])
        if garment_type == "pants":
            waist = self._distance(landmarks["waist_left"], landmarks["waist_right"])
            hip = self._distance(landmarks["hip_left"], landmarks["hip_right"])
            rise = abs(landmarks["crotch_center"][1] - landmarks["garment_top"][1])
            inseam = abs(landmarks["garment_bottom"][1] - landmarks["crotch_center"][1])
            return {
                "garment_length": (length, "vertical_landmark_distance", 0.88),
                "waist_flat_width": (waist, "silhouette_row_width", 0.82),
                "waist_circumference_est": (waist * 2.0, "flat_width_x2", 0.66),
                "hip_flat_width": (hip, "silhouette_row_width", 0.76),
                "hip_circumference_est": (hip * 2.0, "flat_width_x2", 0.62),
                "front_rise": (rise, "landmark_distance", 0.58),
                "inseam": (inseam, "landmark_distance", 0.60),
            }

        waist = self._distance(landmarks["waist_left"], landmarks["waist_right"])
        hem = self._distance(landmarks["hem_left"], landmarks["hem_right"])
        if garment_type == "skirt":
            hip = self._distance(landmarks["hip_left"], landmarks["hip_right"])
            return {
                "garment_length": (length, "vertical_landmark_distance", 0.90),
                "waist_flat_width": (waist, "silhouette_row_width", 0.82),
                "waist_circumference_est": (waist * 2.0, "flat_width_x2", 0.66),
                "hip_flat_width": (hip, "silhouette_row_width", 0.74),
                "hip_circumference_est": (hip * 2.0, "flat_width_x2", 0.60),
                "hem_flat_width": (hem, "silhouette_row_width", 0.80),
            }

        shoulder = self._distance(
            landmarks["left_shoulder"], landmarks["right_shoulder"]
        )
        chest = self._distance(landmarks["left_armpit"], landmarks["right_armpit"])
        sleeve = (
            self._distance(landmarks["left_shoulder"], landmarks["left_sleeve_end"])
            + self._distance(
                landmarks["right_shoulder"], landmarks["right_sleeve_end"]
            )
        ) / 2.0
        armhole = abs(landmarks["left_armpit"][1] - landmarks["left_shoulder"][1])
        neck = self._distance(landmarks["neck_left"], landmarks["neck_right"])
        return {
            "garment_length": (length, "vertical_landmark_distance", 0.90),
            "shoulder_width": (shoulder, "silhouette_landmarks", 0.68),
            "chest_flat_width": (chest, "silhouette_row_width", 0.82),
            "chest_circumference_est": (chest * 2.0, "flat_width_x2", 0.66),
            "waist_flat_width": (waist, "silhouette_row_width", 0.78),
            "waist_circumference_est": (waist * 2.0, "flat_width_x2", 0.62),
            "hem_flat_width": (hem, "silhouette_row_width", 0.80),
            "sleeve_length": (sleeve, "silhouette_landmarks", 0.56),
            "armhole_depth": (armhole, "silhouette_landmarks", 0.54),
            "neck_opening_width": (neck, "inferred_neck_landmarks", 0.48),
        }

    @staticmethod
    def _calibrate_scale(
        measurements: dict[str, tuple[float, str, float]],
        reference_name: str | None,
        reference_value_cm: float | None,
        garment_type: str,
    ) -> dict[str, Any]:
        if reference_name and reference_name in measurements and reference_value_cm:
            pixel_value = measurements[reference_name][0]
            if pixel_value > 0 and 1.0 <= reference_value_cm <= 300.0:
                cm_per_pixel = float(reference_value_cm) / pixel_value
                return {
                    "calibrated": True,
                    "cm_per_pixel": round(cm_per_pixel, 8),
                    "calibrated_from": reference_name,
                    "mesh_meters_per_pixel": cm_per_pixel / 100.0,
                    "mesh_scale_source": "user_reference",
                    "confidence": 0.95,
                }

        height_px = measurements["garment_length"][0]
        meters_per_pixel = DEFAULT_HEIGHT_METERS[garment_type] / max(height_px, 1.0)
        return {
            "calibrated": False,
            "cm_per_pixel": None,
            "calibrated_from": None,
            "mesh_meters_per_pixel": meters_per_pixel,
            "mesh_scale_source": "category_preview_default",
            "confidence": 0.25,
        }

    @staticmethod
    def _measurement_contract(
        measurements: dict[str, tuple[float, str, float]],
        cm_per_pixel: float | None,
        reference_name: str | None,
    ) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for name, (pixels, method, confidence) in measurements.items():
            calibrated = cm_per_pixel is not None
            result[name] = {
                "value_cm": round(pixels * cm_per_pixel, 2) if calibrated else None,
                "value_px": round(pixels, 2),
                "method": method,
                "source": (
                    "user_reference"
                    if calibrated and name == reference_name
                    else "derived_from_calibration"
                    if calibrated
                    else "relative_only"
                ),
                "confidence": round(
                    0.98 if calibrated and name == reference_name else confidence, 2
                ),
            }
        return result

    def _build_mesh(
        self,
        *,
        front_rgb: np.ndarray,
        back_rgb: np.ndarray | None,
        mask: np.ndarray,
        garment_type: str,
        meters_per_pixel: float,
        landmarks: dict[str, tuple[float, float]],
    ) -> dict[str, Any]:
        ys, xs = np.nonzero(mask)
        x0, x1 = float(xs.min()), float(xs.max())
        y0, y1 = float(ys.min()), float(ys.max())
        box_width = max(1.0, x1 - x0)
        box_height = max(1.0, y1 - y0)
        center_x = (x0 + x1) / 2.0
        center_y = (y0 + y1) / 2.0

        # ── Smooth the mask before grid generation ──────────────────────────────
        # Gaussian blur + threshold + morphological close produces a continuous,
        # clean silhouette without single-pixel staircase or noise.
        _blur = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), sigmaX=3.0, sigmaY=3.0)
        _m8 = (_blur > 0.45).astype(np.uint8)
        _sm_k = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (max(5, int(box_width * 0.018)), max(5, int(box_height * 0.018))),
        )
        _m8 = cv2.morphologyEx(_m8, cv2.MORPH_CLOSE, _sm_k, iterations=2)
        mesh_mask: np.ndarray = _m8.astype(bool)
        # ────────────────────────────────────────────────────────────────────────

        nx = self.grid_resolution
        ny = max(24, int(round(nx * box_height / box_width)))
        ny = min(ny, self.grid_resolution * 2)
        grid_x = np.linspace(x0, x1, nx + 1)
        grid_y = np.linspace(y0, y1, ny + 1)

        def row_extent(pixel_y: float) -> tuple[float, float]:
            target = min(max(int(round(pixel_y)), 0), mesh_mask.shape[0] - 1)
            for offset in range(0, max(3, int(box_height * 0.04))):
                for candidate in (target + offset, target - offset):
                    if 0 <= candidate < mesh_mask.shape[0]:
                        values = np.flatnonzero(mesh_mask[candidate])
                        if len(values) >= 2:
                            return float(values.min()), float(values.max())
            return x0, x1

        def col_extent(pixel_x: float) -> tuple[float, float]:
            target = min(max(int(round(pixel_x)), 0), mesh_mask.shape[1] - 1)
            for offset in range(0, max(3, int(box_width * 0.04))):
                for candidate in (target + offset, target - offset):
                    if 0 <= candidate < mesh_mask.shape[1]:
                        values = np.flatnonzero(mesh_mask[:, candidate])
                        if len(values) >= 2:
                            return float(values.min()), float(values.max())
            return y0, y1

        is_top = garment_type in {"tshirt", "shirt", "jacket", "dress"}
        crotch_y = landmarks.get("crotch_center", (center_x, y0 + box_height * 0.45))[1]

        if garment_type in {"pants", "skirt"}:
            hip_l = landmarks.get("hip_left", (x0 + box_width * 0.25, y0 + box_height * 0.25))
            hip_r = landmarks.get("hip_right", (x1 - box_width * 0.25, y0 + box_height * 0.25))
            torso_w_px = max(1.0, abs(hip_r[0] - hip_l[0]))
            torso_w_m = torso_w_px * meters_per_pixel
            base_depth = max(0.055, min(0.12, torso_w_m * 0.24))
            left_armpit_x = x0
            right_armpit_x = x1
            sleeve_span_left = 1.0
            sleeve_span_right = 1.0
            z_shoulder = base_depth
            z_cuff = base_depth
        else:
            armpit_l = landmarks.get("left_armpit", (center_x - box_width * 0.26, y0 + box_height * 0.38))
            armpit_r = landmarks.get("right_armpit", (center_x + box_width * 0.26, y0 + box_height * 0.38))
            waist_l = landmarks.get("waist_left", (center_x - box_width * 0.24, y0 + box_height * 0.70))
            waist_r = landmarks.get("waist_right", (center_x + box_width * 0.24, y0 + box_height * 0.70))
            chest_w_px = abs(armpit_r[0] - armpit_l[0])
            waist_w_px = abs(waist_r[0] - waist_l[0])
            torso_w_px = max(1.0, max(chest_w_px, waist_w_px))
            torso_w_m = torso_w_px * meters_per_pixel
            # Tailored slim depth: ~5.6-6.4 cm total thickness (half-depth ~2.8-3.2 cm)
            # User requirement: "giảm độ rộng của áo xuống đáng kể", "form hiện tại khá đẹp rồi đừng chỉnh thêm gì nữa"
            body_depth = max(0.026, min(0.034, torso_w_m * 0.068))
            base_depth = body_depth
            # Shoulder apex ridge: ~1 cm total thickness (half-depth 0.005 m = 0.5 cm)
            z_apex = 0.005
            # Edge thickness at silhouette seams: 1.2 mm (total thickness 2.4 mm)
            # Continuous elliptical curve all the way to 1.2 mm so edges are softly rounded without flat 90-degree step walls
            z_edge = 0.0012
            left_armpit_x = armpit_l[0]
            right_armpit_x = armpit_r[0]
            armpit_y = min(armpit_l[1], armpit_r[1])
            sleeve_span_left = max(1.0, left_armpit_x - x0)
            sleeve_span_right = max(1.0, x1 - right_armpit_x)
            z_shoulder = body_depth * 0.60
            z_cuff = body_depth * 0.40

        def get_depth_factor(v: float) -> float:
            if garment_type in {"pants", "skirt"}:
                if v < 0.15:
                    return 0.70 + 0.30 * (v / 0.15)
                elif v < 0.45:
                    return 1.0
                else:
                    return 1.0 - 0.40 * ((v - 0.45) / 0.55)
            else:
                if v < 0.14:
                    return 0.28 + 0.20 * (v / 0.14)
                elif v < 0.42:
                    t = (v - 0.14) / 0.28
                    return 0.48 + 0.52 * math.sin(t * (math.pi / 2.0))
                elif v < 0.72:
                    t = (v - 0.42) / 0.30
                    return 1.0 - 0.12 * t
                else:
                    t = (v - 0.72) / 0.28
                    return 0.88 - 0.08 * t

        # ── Collar Opening Dimensions & Parameters ───────────────────────────
        # Crew-neck collar: shallow & raised high (~2.6-3.0 cm on a 70 cm shirt)
        collar_half_w_px = max(1.0, min(box_width * 0.12, torso_w_px * 0.20))
        collar_drop_y_px = max(4.0, box_height * 0.038)
        collar_radius_x_m = max(0.068, min(0.085, collar_half_w_px * meters_per_pixel))
        neck_opening = (center_x, y0, collar_half_w_px, collar_drop_y_px, box_height)

        def is_in_neck_opening(test_px: float, test_py: float) -> bool:
            if not is_top:
                return False
            dx = abs(test_px - center_x)
            if dx >= collar_half_w_px:
                return False
            u = dx / collar_half_w_px
            y_cut = y0 + collar_drop_y_px * math.sqrt(max(0.0, 1.0 - u * u))
            return test_py < y_cut

        def get_z_at(test_px: float, test_py: float) -> float:
            if not is_top:
                rel_y = max(0.0, min(1.0, (test_py - y0) / box_height))
                depth_factor = get_depth_factor(rel_y)
                peak_z = base_depth * depth_factor
                edge_z = max(0.005, min(0.012, peak_z * 0.12))
                if garment_type == "pants" and test_py > crotch_y:
                    row_l, row_r = row_extent(test_py)
                    if test_px < center_x:
                        leg_center = (row_l + center_x) / 2.0
                        leg_half_w = max((center_x - row_l) / 2.0, 1.0)
                    else:
                        leg_center = (center_x + row_r) / 2.0
                        leg_half_w = max((row_r - center_x) / 2.0, 1.0)
                    norm_x = max(-1.0, min(1.0, (test_px - leg_center) / leg_half_w))
                    curvature = math.sqrt(max(0.0, 1.0 - norm_x**2))
                    return edge_z + (peak_z - edge_z) * curvature
                col_top, col_bot = col_extent(test_px)
                col_h = max(col_bot - col_top, 1.0)
                col_cy = (col_top + col_bot) / 2.0
                norm_y = max(-1.0, min(1.0, (test_py - col_cy) / (col_h / 2.0)))
                curvature = math.sqrt(max(0.0, 1.0 - norm_y**2))
                return edge_z + (peak_z - edge_z) * curvature

            # ── TOPS: Organic Curvature, Rounded Elliptical Edges & Soft Drape ───
            # User requirement: "cạnh của thân áo và tay áo cong cong 1 tí như cạnh hình elip"
            # Eliminates boxy 90-degree step walls by tapering horizontally & vertically to z_edge = 1.2 mm
            if test_py >= armpit_y:
                # ── Lower Torso: Exact Horizontal Ellipse Across Silhouette ────────
                # At any height below armpits down to hem, row_extent(test_py) gives the
                # actual left and right silhouette boundaries (row_l, row_r).
                row_l, row_r = row_extent(test_py)
                row_w = max(1.0, row_r - row_l)
                row_cx = (row_l + row_r) / 2.0
                u = min(1.0, max(0.0, abs(test_px - row_cx) / (row_w / 2.0)))
                curve_x = math.sqrt(max(0.0, 1.0 - u * u))
                horiz_z = z_edge + (body_depth - z_edge) * curve_x

                # Straight vertical drape below chest with soft natural micro-ripples
                rel_y = max(0.0, min(1.0, (test_py - armpit_y) / max(1.0, y1 - armpit_y)))
                drape = 1.0 - 0.03 * math.sin(rel_y * math.pi) + 0.015 * math.sin(u * math.pi * 3.0) * rel_y
                return max(z_edge, horiz_z * drape)

            # Above armpit_y: Upper Torso (Chest/Shoulders) and Sleeves
            frac_y = max(0.0, min(1.0, (test_py - y0) / max(1.0, armpit_y - y0)))
            shoulder_half = torso_w_px * 0.37
            armhole_l = (center_x - shoulder_half) * (1.0 - frac_y) + left_armpit_x * frac_y
            armhole_r = (center_x + shoulder_half) * (1.0 - frac_y) + right_armpit_x * frac_y

            if armhole_l <= test_px <= armhole_r:
                # ── Upper Torso: Smooth Chest Ellipse & Shoulder Cone Slope ────────
                torso_half = max(1.0, (armhole_r - armhole_l) / 2.0)
                torso_cx = (armhole_l + armhole_r) / 2.0
                u = min(1.0, max(0.0, abs(test_px - torso_cx) / torso_half))
                curve_x = math.sqrt(max(0.0, 1.0 - u * u))
                # Smooth transition: center has body_depth, armholes blend to z_shoulder
                torso_peak_z = z_shoulder + (body_depth - z_shoulder) * curve_x
                # Shoulder cone slope: slopes up to 1 cm apex at y0 (no collar bulge)
                vert_factor = 0.35 + 0.65 * math.sin(frac_y * (math.pi / 2.0))
                return max(z_apex, torso_peak_z * vert_factor)
            else:
                # ── Sleeves: Rounded 3D Elliptical Tubes with Elliptical Cuff ──────
                if test_px < armhole_l:
                    span = max(1.0, armhole_l - x0)
                    u_sleeve = min(1.0, max(0.0, (armhole_l - test_px) / span))
                else:
                    span = max(1.0, x1 - armhole_r)
                    u_sleeve = min(1.0, max(0.0, (test_px - armhole_r) / span))

                # Vertical elliptical curvature across the arm tube (norm_y = ±1 at top/bottom seams)
                col_top, col_bot = col_extent(test_px)
                col_h = max(col_bot - col_top, 1.0)
                col_cy = (col_top + col_bot) / 2.0
                norm_y = max(-1.0, min(1.0, (test_py - col_cy) / (col_h / 2.0)))
                tube_curve = math.sqrt(max(0.0, 1.0 - norm_y * norm_y))

                # Base depth along sleeve: gently tapers from shoulder to cuff
                sleeve_base_z = z_shoulder - u_sleeve * (z_shoulder - z_cuff)

                # Elliptical cuff rounding in X: curves softly down to z_edge at the cuff edge
                # for the distal 65% of the sleeve, eliminating boxy vertical flat ends
                if u_sleeve <= 0.30:
                    cuff_round = 1.0
                else:
                    w = (u_sleeve - 0.30) / 0.70
                    cuff_round = math.sqrt(max(0.0, 1.0 - w * w))

                peak_sleeve_z = z_edge + (sleeve_base_z - z_edge) * cuff_round
                return max(z_edge, z_edge + (peak_sleeve_z - z_edge) * tube_curve)

        cell_faces: list[tuple[int, int, tuple[tuple[int, int], ...]]] = []
        for row in range(ny):
            for column in range(nx):
                corners = (
                    (row, column),
                    (row + 1, column),
                    (row, column + 1),
                    (row + 1, column + 1),
                )
                for face in (
                    (corners[0], corners[1], corners[2]),
                    (corners[2], corners[1], corners[3]),
                ):
                    px = int(round(np.mean([grid_x[node[1]] for node in face])))
                    py = int(round(np.mean([grid_y[node[0]] for node in face])))
                    px = min(max(px, 0), mesh_mask.shape[1] - 1)
                    py = min(max(py, 0), mesh_mask.shape[0] - 1)
                    if mesh_mask[py, px] and not is_in_neck_opening(px, py):
                        cell_faces.append((row, column, face))
        if len(cell_faces) < 24:
            raise ReconstructionError(
                "GARMENT_MESH_TOO_SPARSE",
                "The segmented garment is too small to reconstruct",
                http_status=422,
            )

        nodes = sorted(
            {
                node
                for _row, _column, face in cell_faces
                for node in face
            }
        )
        node_index = {node: index for index, node in enumerate(nodes)}

        front_faces: list[tuple[int, int, int]] = []
        back_faces: list[tuple[int, int, int]] = []
        for _row, _column, (first, second, third) in cell_faces:
            front_faces.append(
                (node_index[first], node_index[second], node_index[third])
            )
            back_faces.append(
                (node_index[first], node_index[third], node_index[second])
            )

        boundary_edges = self._boundary_edges(front_faces)

        # ── Smooth Boundary Vertices (Eliminates staircase saw-teeth on silhouette) ─
        raw_pixels = [(float(grid_x[column]), float(grid_y[row])) for row, column in nodes]
        boundary_adj: dict[int, list[int]] = {}
        for u, v in boundary_edges:
            boundary_adj.setdefault(u, []).append(v)
            boundary_adj.setdefault(v, []).append(u)

        node_pixels = list(raw_pixels)
        for _ in range(4):
            prev = list(node_pixels)
            for idx, neighbors in boundary_adj.items():
                if len(neighbors) == 2:
                    n1, n2 = neighbors
                    node_pixels[idx] = (
                        0.5 * prev[idx][0] + 0.25 * (prev[n1][0] + prev[n2][0]),
                        0.5 * prev[idx][1] + 0.25 * (prev[n1][1] + prev[n2][1]),
                    )
        # ────────────────────────────────────────────────────────────────────────

        front_vertices = []
        back_vertices = []
        uvs = []
        for index, (row, column) in enumerate(nodes):
            px, py = node_pixels[index]
            z = get_z_at(px, py)
            x = (px - center_x) * meters_per_pixel
            y = (center_y - py) * meters_per_pixel
            front_vertices.append((x, y, z))
            back_vertices.append((x, y, -z))
            uvs.append((px / max(1, mask.shape[1] - 1), 1.0 - py / max(1, mask.shape[0] - 1)))

        seam_vertices: list[tuple[float, float, float]] = []
        seam_uvs: list[tuple[float, float]] = []
        seam_faces: list[tuple[int, int, int]] = []
        opening_vertices: dict[str, set[int]] = {}
        for first, second in boundary_edges:
            p1 = node_pixels[first]
            p2 = node_pixels[second]
            midpoint = (
                (p1[0] + p2[0]) / 2.0,
                (p1[1] + p2[1]) / 2.0,
            )
            edge_vec = (p2[0] - p1[0], p2[1] - p1[1])
            # Directed boundary edge normal: (-dy, dx) in screen coordinates (+Y down)
            norm_x = -(p2[1] - p1[1])
            norm_y = (p2[0] - p1[0])
            n_len = math.hypot(norm_x, norm_y)
            if n_len > 1e-6:
                norm_x /= n_len
                norm_y /= n_len
            test_d = max(3.0, box_width / float(self.grid_resolution))
            out_px = int(round(midpoint[0] + norm_x * test_d))
            out_py = int(round(midpoint[1] + norm_y * test_d))
            in_px = int(round(midpoint[0] - norm_x * test_d))
            in_py = int(round(midpoint[1] - norm_y * test_d))
            h_m, w_m = mesh_mask.shape
            out_px = min(max(out_px, 0), w_m - 1)
            out_py = min(max(out_py, 0), h_m - 1)
            in_px = min(max(in_px, 0), w_m - 1)
            in_py = min(max(in_py, 0), h_m - 1)
            if mesh_mask[out_py, out_px] and not mesh_mask[in_py, in_px]:
                norm_x, norm_y = -norm_x, -norm_y

            opening = self._opening_name(
                midpoint,
                garment_type,
                x0=x0,
                x1=x1,
                y0=y0,
                y1=y1,
                landmarks=landmarks,
                neck_opening=neck_opening,
                edge_vec=edge_vec,
                normal=(norm_x, norm_y),
            )
            if opening:
                opening_vertices.setdefault(opening, set()).update((first, second))
                # Collar opening and bottom hem are left COMPLETELY HOLLOW and unbridged!
                # Looking down through the collar from above, the user sees through
                # the inside of the shirt to the white canvas background (white ellipse)!
                if opening in {"neck", "hem", "waist", "left_hem", "right_hem"}:
                    continue
            # Bridge every closed silhouette edge (including cuffs and shoulders) with a continuous fabric wall.
            base = len(seam_vertices)
            seam_vertices.extend(
                (
                    front_vertices[first],
                    front_vertices[second],
                    back_vertices[second],
                    back_vertices[first],
                )
            )
            seam_uvs.extend(
                (
                    (0.0, 0.0),
                    (1.0, 0.0),
                    (1.0, 1.0),
                    (0.0, 1.0),
                )
            )
            seam_faces.extend(((base, base + 1, base + 2), (base, base + 2, base + 3)))

        front_mesh = trimesh.Trimesh(
            vertices=np.asarray(front_vertices),
            faces=np.asarray(front_faces),
            process=False,
        )
        _ = front_mesh.vertex_normals

        # Defringe: wipe white background bleed / white side-border lines with fabric_color.
        # Central artwork region (e.g. "DAVIES" graphic) is preserved.
        fabric_color = np.median(front_rgb[mask], axis=0).astype(np.uint8)
        clean_front_rgb = front_rgb.copy()
        clean_front_rgb[~mask] = fabric_color

        kernel = np.ones((5, 5), dtype=np.uint8)
        eroded_mask = cv2.erode(mask.astype(np.uint8), kernel, iterations=4)
        border_band = mask & (eroded_mask == 0)
        # Overwrite the entire silhouette border band with fabric_color
        clean_front_rgb[border_band] = fabric_color

        # Clean collar cutout area: wipe out any neck tags, inner collar ribbing or white fringes
        if garment_type in {"tshirt", "shirt", "jacket", "dress"}:
            neck_y_max = int(round(y0 + collar_drop_y_px + box_height * 0.04))
            for ny_idx in range(int(round(y0)), min(neck_y_max, mask.shape[0])):
                for nx_idx in range(max(0, int(center_x - collar_half_w_px * 1.25)), min(mask.shape[1], int(center_x + collar_half_w_px * 1.25))):
                    if is_in_neck_opening(float(nx_idx), float(ny_idx) + 8.0):
                        clean_front_rgb[ny_idx, nx_idx] = fabric_color

        # Outside the central artwork zone, kill any remaining bright lines/specs
        art_y0 = max(0, int(y0 + box_height * 0.22))
        art_y1 = min(mask.shape[0], int(y0 + box_height * 0.50))
        art_x0 = max(0, int(center_x - box_width * 0.28))
        art_x1 = min(mask.shape[1], int(center_x + box_width * 0.28))
        outside_art = np.ones(mask.shape, dtype=bool)
        outside_art[art_y0:art_y1, art_x0:art_x1] = False

        # Any non-fabric pixels (white background bleed, neck tags, noisy speckles) outside art zone -> fabric_color
        color_diff = np.linalg.norm(clean_front_rgb.astype(np.float32) - fabric_color.astype(np.float32), axis=2)
        non_fabric_outside = mask & outside_art & (color_diff > 14.0)
        clean_front_rgb[non_fabric_outside] = fabric_color

        # Dilate fill so UV bilinear interpolation never reaches white background
        dilated_mask = cv2.dilate(mask.astype(np.uint8), kernel, iterations=4)
        clean_front_rgb[~mask] = fabric_color
        clean_front_rgb[dilated_mask == 0] = fabric_color

        front_material = trimesh.visual.material.PBRMaterial(
            baseColorFactor=[1.0, 1.0, 1.0, 1.0],
            baseColorTexture=Image.fromarray(clean_front_rgb),
            metallicFactor=0.0,
            roughnessFactor=0.92,
            doubleSided=True,
        )
        front_mesh.visual = trimesh.visual.texture.TextureVisuals(
            uv=np.asarray(uvs), material=front_material
        )

        back_mesh = trimesh.Trimesh(
            vertices=np.asarray(back_vertices),
            faces=np.asarray(back_faces),
            process=False,
        )
        _ = back_mesh.vertex_normals
        if back_rgb is not None:
            clean_back = back_rgb.copy()
            clean_back[~mask] = fabric_color
            clean_back[border_band] = fabric_color
            clean_back[~eroded_mask.astype(bool)] = fabric_color
            back_texture_img = clean_back
        else:
            # Mirror defringe: plain fabric color on back (no artwork from single photo).
            back_texture_img = np.empty_like(clean_front_rgb)
            back_texture_img[:] = fabric_color

        back_material = trimesh.visual.material.PBRMaterial(
            baseColorFactor=[1.0, 1.0, 1.0, 1.0],
            baseColorTexture=Image.fromarray(back_texture_img),
            metallicFactor=0.0,
            roughnessFactor=0.92,
            doubleSided=True,
        )
        back_mesh.visual = trimesh.visual.texture.TextureVisuals(
            uv=np.asarray(uvs), material=back_material
        )

        scene = trimesh.Scene()
        scene.add_geometry(front_mesh, node_name="GarmentFront", geom_name="GarmentFront")
        scene.add_geometry(back_mesh, node_name="GarmentBack", geom_name="GarmentBack")

        if seam_faces:
            seam_mesh = trimesh.Trimesh(
                vertices=np.asarray(seam_vertices),
                faces=np.asarray(seam_faces),
                process=False,
            )
            _ = seam_mesh.vertex_normals
            # 16×16 solid fabric_color tile — Three.js renders seams identical to fabric panels.
            seam_color_img = np.zeros((16, 16, 3), dtype=np.uint8)
            seam_color_img[:] = fabric_color
            seam_texture = Image.fromarray(seam_color_img)
            seam_material = trimesh.visual.material.PBRMaterial(
                baseColorFactor=[1.0, 1.0, 1.0, 1.0],
                baseColorTexture=seam_texture,
                metallicFactor=0.0,
                roughnessFactor=0.92,
                doubleSided=True,
            )
            seam_mesh.visual = trimesh.visual.texture.TextureVisuals(
                uv=np.asarray(seam_uvs, dtype=np.float32),
                material=seam_material,
            )
            scene.add_geometry(
                seam_mesh, node_name="GarmentSeams", geom_name="GarmentSeams"
            )

        landmark_vertices: dict[str, dict[str, Any]] = {}
        pixel_array = np.asarray(node_pixels)
        for name, point in landmarks.items():
            nearest = int(np.argmin(np.sum((pixel_array - np.asarray(point)) ** 2, axis=1)))
            landmark_vertices[name] = {
                "front_vertex": nearest,
                "back_vertex": nearest,
                "front_position_m": [round(float(value), 6) for value in front_vertices[nearest]],
                "back_position_m": [round(float(value), 6) for value in back_vertices[nearest]],
            }

        openings = {
            name: {
                "mesh_nodes": ["GarmentFront", "GarmentBack"],
                "vertex_indices": sorted(indices),
            }
            for name, indices in opening_vertices.items()
        }
        return {
            "scene": scene,
            "front_vertex_count": len(front_vertices),
            "back_vertex_count": len(back_vertices),
            "triangle_count": len(front_faces) + len(back_faces) + len(seam_faces),
            "landmark_vertices": landmark_vertices,
            "openings": openings,
        }

    @staticmethod
    def _boundary_edges(faces: list[tuple[int, int, int]]) -> list[tuple[int, int]]:
        counts: dict[tuple[int, int], int] = {}
        orientation: dict[tuple[int, int], tuple[int, int]] = {}
        for face in faces:
            for first, second in (
                (face[0], face[1]),
                (face[1], face[2]),
                (face[2], face[0]),
            ):
                key = tuple(sorted((first, second)))
                counts[key] = counts.get(key, 0) + 1
                orientation[key] = (first, second)
        return [orientation[key] for key, count in counts.items() if count == 1]

    @staticmethod
    def _opening_name(
        point: tuple[float, float],
        garment_type: str,
        *,
        x0: float,
        x1: float,
        y0: float,
        y1: float,
        landmarks: dict[str, tuple[float, float]],
        neck_opening: tuple[float, float, float, float, float],
        edge_vec: tuple[float, float] = (0.0, 0.0),
        normal: tuple[float, float] = (0.0, 0.0),
    ) -> str | None:
        normalized_x = (point[0] - x0) / max(1.0, x1 - x0)
        normalized_y = (point[1] - y0) / max(1.0, y1 - y0)
        width = max(1.0, x1 - x0)
        height = max(1.0, y1 - y0)

        if garment_type == "pants":
            if normalized_y < 0.08:
                return "waist"
            if normalized_y > 0.90:
                return "left_hem" if normalized_x < 0.5 else "right_hem"
            return None

        if garment_type == "skirt":
            if normalized_y < 0.08:
                return "waist"
            if normalized_y > 0.90:
                return "hem"
            return None

        # Tops (tshirt, shirt, jacket, dress):
        # 1. Neck opening
        center_x, top_y, collar_half_w, collar_drop_y, box_h = neck_opening
        dx = abs(point[0] - center_x)
        if dx < collar_half_w * 1.08:
            u = min(1.0, dx / collar_half_w)
            y_cut = top_y + collar_drop_y * math.sqrt(max(0.0, 1.0 - u * u))
            if point[1] <= y_cut + max(6.0, width * 0.02):
                return "neck"

        # 2. Sleeve cuff openings ─────────────────────────────────────────────
        # Crucial: ONLY the outer distal end of the sleeve is an opening (left unseamed).
        # The top seam (shoulder -> cuff) and underarm seam (cuff -> armpit) MUST be seamed!
        # When top and underarm seams are closed, leaving only the cuff open creates
        # a smooth, hollow elliptical cylinder through which the user sees the background.
        left_armpit = landmarks.get("left_armpit")
        right_armpit = landmarks.get("right_armpit")
        norm_x, norm_y = normal

        if left_armpit is not None:
            sleeve_len_x = left_armpit[0] - x0
            if point[0] <= x0 + sleeve_len_x * 0.50:
                # Must be an outward-facing end edge (pointing LEFT), NOT top (pointing UP) or underarm (pointing DOWN)
                if norm_x < -0.30 or (norm_x == 0.0 and abs(edge_vec[1]) >= abs(edge_vec[0])):
                    return "left_cuff"

        if right_armpit is not None:
            sleeve_len_x = x1 - right_armpit[0]
            if point[0] >= x1 - sleeve_len_x * 0.50:
                # Must be an outward-facing end edge (pointing RIGHT)
                if norm_x > 0.30 or (norm_x == 0.0 and abs(edge_vec[1]) >= abs(edge_vec[0])):
                    return "right_cuff"

        # 3. Bottom hem opening ────────────────────────────────────────────────
        # Only horizontal bottom edges are hem openings. Vertical side edges at the
        # bottom corners belong to the side seam and MUST be seamed so there is NO slit!
        waist_left = landmarks.get("waist_left", (x0 + width * 0.20, y1))
        waist_right = landmarks.get("waist_right", (x1 - width * 0.20, y1))
        torso_left = min(waist_left[0], landmarks.get("hem_left", waist_left)[0])
        torso_right = max(waist_right[0], landmarks.get("hem_right", waist_right)[0])

        if point[1] >= y1 - max(8.0, height * 0.04):
            # Must be downward-facing (horizontal edge):
            if (norm_y > 0.40 and norm_y > abs(norm_x)) or (norm_y == 0.0 and abs(edge_vec[0]) >= abs(edge_vec[1])):
                # Must be within torso width (not past the side seam):
                if torso_left + max(4.0, width * 0.015) <= point[0] <= torso_right - max(4.0, width * 0.015):
                    return "hem"

        return None

    @staticmethod
    def _landmark_contract(
        landmarks: dict[str, tuple[float, float]],
        vertices: dict[str, dict[str, Any]],
        mask: np.ndarray,
    ) -> dict[str, dict[str, Any]]:
        height, width = mask.shape

        def is_visible(point: tuple[float, float]) -> bool:
            x, y = int(round(point[0])), int(round(point[1]))
            x0, x1 = max(0, x - 3), min(width, x + 4)
            y0, y1 = max(0, y - 3), min(height, y + 4)
            return bool(mask[y0:y1, x0:x1].any())

        return {
            name: {
                "image_px": [round(point[0], 2), round(point[1], 2)],
                "image_normalized": [
                    round(point[0] / max(1, width - 1), 6),
                    round(point[1] / max(1, height - 1), 6),
                ],
                **vertices[name],
                "source": "silhouette_inferred",
                "annotation_visible": is_visible(point),
            }
            for name, point in landmarks.items()
        }

    @staticmethod
    def _attachment_regions(
        garment_type: str, landmarks: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        if garment_type in {"pants", "skirt"}:
            mapping = {
                "waist": ["waist_left", "waist_right"],
                "hips": ["hip_left", "hip_right"],
            }
        else:
            mapping = {
                "shoulders": ["left_shoulder", "right_shoulder"],
                "chest": ["left_armpit", "right_armpit"],
                "waist": ["waist_left", "waist_right"],
                "left_arm": ["left_shoulder", "left_sleeve_end"],
                "right_arm": ["right_shoulder", "right_sleeve_end"],
            }
        return {
            region: {
                "body_region": region,
                "landmarks": names,
                "front_vertex_indices": [
                    landmarks[name]["front_vertex"]
                    for name in names
                    if name in landmarks
                ],
                "recommended_clearance_cm": 1.0 if region != "waist" else 0.8,
            }
            for region, names in mapping.items()
        }

    @staticmethod
    def _save_preview(rgb: np.ndarray, mask: np.ndarray, destination: Path) -> None:
        alpha = (mask.astype(np.uint8) * 255)[:, :, None]
        rgba = np.concatenate((rgb, alpha), axis=2)
        Image.fromarray(rgba, mode="RGBA").save(destination, format="PNG")
