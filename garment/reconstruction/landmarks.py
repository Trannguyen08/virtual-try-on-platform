from __future__ import annotations

import math
from typing import Any

import numpy as np

from .errors import ReconstructionError

DEFAULT_HEIGHT_METERS = {
    "tshirt": 0.68,
    "shirt": 0.72,
    "jacket": 0.74,
    "pants": 1.02,
    "skirt": 0.65,
    "dress": 1.10,
}


def detect_landmarks(
    mask: np.ndarray, garment_type: str
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


def compute_distance(
    first: tuple[float, float], second: tuple[float, float]
) -> float:
    return math.dist(first, second)


def compute_measurements(
    landmarks: dict[str, tuple[float, float]],
    garment_type: str,
) -> dict[str, tuple[float, str, float]]:
    length = compute_distance(landmarks["garment_top"], landmarks["garment_bottom"])
    if garment_type == "pants":
        waist = compute_distance(landmarks["waist_left"], landmarks["waist_right"])
        hip = compute_distance(landmarks["hip_left"], landmarks["hip_right"])
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

    waist = compute_distance(landmarks["waist_left"], landmarks["waist_right"])
    hem = compute_distance(landmarks["hem_left"], landmarks["hem_right"])
    if garment_type == "skirt":
        hip = compute_distance(landmarks["hip_left"], landmarks["hip_right"])
        return {
            "garment_length": (length, "vertical_landmark_distance", 0.90),
            "waist_flat_width": (waist, "silhouette_row_width", 0.82),
            "waist_circumference_est": (waist * 2.0, "flat_width_x2", 0.66),
            "hip_flat_width": (hip, "silhouette_row_width", 0.74),
            "hip_circumference_est": (hip * 2.0, "flat_width_x2", 0.60),
            "hem_flat_width": (hem, "silhouette_row_width", 0.80),
        }

    shoulder = compute_distance(
        landmarks["left_shoulder"], landmarks["right_shoulder"]
    )
    chest = compute_distance(landmarks["left_armpit"], landmarks["right_armpit"])
    sleeve = (
        compute_distance(landmarks["left_shoulder"], landmarks["left_sleeve_end"])
        + compute_distance(
            landmarks["right_shoulder"], landmarks["right_sleeve_end"]
        )
    ) / 2.0
    armhole = abs(landmarks["left_armpit"][1] - landmarks["left_shoulder"][1])
    neck = compute_distance(landmarks["neck_left"], landmarks["neck_right"])
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


def calibrate_scale(
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
    effective_type = garment_type if garment_type in DEFAULT_HEIGHT_METERS else "tshirt"
    meters_per_pixel = DEFAULT_HEIGHT_METERS[effective_type] / max(height_px, 1.0)
    return {
        "calibrated": False,
        "cm_per_pixel": None,
        "calibrated_from": None,
        "mesh_meters_per_pixel": meters_per_pixel,
        "mesh_scale_source": "category_preview_default",
        "confidence": 0.25,
    }


def build_measurement_contract(
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


def build_landmark_contract(
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
            "front_vertex": vertices.get(name, {}).get("front_vertex"),
            "back_vertex": vertices.get(name, {}).get("back_vertex"),
            "front_position_m": vertices.get(name, {}).get("front_position_m"),
            "back_position_m": vertices.get(name, {}).get("back_position_m"),
            "source": "silhouette_geometry",
            "annotation_visible": is_visible(point),
        }
        for name, point in landmarks.items()
    }


def build_attachment_regions(
    garment_type: str, landmark_vertices: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    def vertex_for(name: str) -> int | None:
        return landmark_vertices.get(name, {}).get("front_vertex")

    if garment_type == "pants":
        return {
            "waist": {
                "body_region": "waist",
                "landmarks": ["waist_left", "waist_right"],
                "front_vertex_indices": [
                    idx
                    for idx in (
                        vertex_for("waist_left"),
                        vertex_for("waist_right"),
                    )
                    if idx is not None
                ],
                "recommended_clearance_cm": 1.2,
            },
            "hips": {
                "body_region": "hips",
                "landmarks": ["hip_left", "hip_right"],
                "front_vertex_indices": [
                    idx
                    for idx in (
                        vertex_for("hip_left"),
                        vertex_for("hip_right"),
                    )
                    if idx is not None
                ],
                "recommended_clearance_cm": 1.5,
            },
        }

    return {
        "shoulders": {
            "body_region": "shoulders",
            "landmarks": ["left_shoulder", "right_shoulder"],
            "front_vertex_indices": [
                idx
                for idx in (
                    vertex_for("left_shoulder"),
                    vertex_for("right_shoulder"),
                )
                if idx is not None
            ],
            "recommended_clearance_cm": 1.0,
        },
        "chest": {
            "body_region": "chest",
            "landmarks": ["left_armpit", "right_armpit"],
            "front_vertex_indices": [
                idx
                for idx in (
                    vertex_for("left_armpit"),
                    vertex_for("right_armpit"),
                )
                if idx is not None
            ],
            "recommended_clearance_cm": 1.8,
        },
        "waist": {
            "body_region": "waist",
            "landmarks": ["waist_left", "waist_right"],
            "front_vertex_indices": [
                idx
                for idx in (
                    vertex_for("waist_left"),
                    vertex_for("waist_right"),
                )
                if idx is not None
            ],
            "recommended_clearance_cm": 2.0,
        },
    }
