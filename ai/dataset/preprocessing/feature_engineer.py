"""Feature Engineering & Data Cleaning Module for Module M4.

Provides domain-specific anthropometric proportions and apparel-body interaction metrics,
with numerical stabilization and measurement rounding to standard 1mm (0.1 cm) precision.
"""

from typing import Any, Dict, List, Union
import numpy as np
import pandas as pd

# ==============================================================================
# FEATURE CONSTANTS
# ==============================================================================
RAW_MEASUREMENT_COLS: List[str] = [
    "body_bust",
    "body_height",
    "body_hips",
    "body_waist",
    "garment_bust",
    "garment_length",
]

INTERACTION_COLS: List[str] = [
    "bust_diff",
    "ease_ratio",
    "length_to_height",
    "abs_optimal_delta",
    "is_negative_ease",
]

ANTHROPOMETRIC_COLS: List[str] = [
    "bust_to_waist",
    "bust_to_hip",
    "waist_to_hip",
    "body_frame_index",
]

ALL_FEATURE_COLS: List[str] = (
    RAW_MEASUREMENT_COLS + INTERACTION_COLS + ANTHROPOMETRIC_COLS
)


# ==============================================================================
# CORE FEATURE EXTRACTION
# ==============================================================================
def clean_measurements(df: pd.DataFrame) -> pd.DataFrame:
    """Loại bỏ các cột đường dẫn thừa và làm tròn số đo về 0.1 cm (1 mm).

    Args:
        df: DataFrame chứa dữ liệu thô.

    Returns:
        DataFrame đã được dọn sạch cột thừa và làm tròn số học.
    """
    clean_df = df.copy()

    # 1. Loại bỏ các cột đường dẫn ảnh không dùng cho mô hình
    cols_to_drop = [c for c in ["cloth_path", "target_path"] if c in clean_df.columns]
    if cols_to_drop:
        clean_df = clean_df.drop(columns=cols_to_drop)

    # 2. Làm tròn các số đo thô về 1 chữ số thập phân (chuẩn may mặc 0.1cm)
    for col in RAW_MEASUREMENT_COLS + ["garment_sleeve_length"]:
        if col in clean_df.columns:
            clean_df[col] = clean_df[col].round(1)

    return clean_df


def extract_fit_features(df: pd.DataFrame) -> pd.DataFrame:
    """Trích xuất 15 đặc trưng hình học & nhân trắc học từ số đo cơ thể và áo.

    Args:
        df: DataFrame chứa các cột số đo cơ bản.

    Returns:
        DataFrame đã bổ sung đầy đủ các đặc trưng tương tác và tỷ lệ vóc dáng.
    """
    data = clean_measurements(df)

    # 1. Tương tác Người <-> Áo (Ease Metrics)
    if "bust_diff" not in data.columns:
        data["bust_diff"] = (data["garment_bust"] - data["body_bust"]).round(1)
    else:
        data["bust_diff"] = data["bust_diff"].round(1)

    data["ease_ratio"] = (data["garment_bust"] / (data["body_bust"] + 1e-6)).round(3)
    data["length_to_height"] = (data["garment_length"] / (data["body_height"] + 1e-6)).round(3)
    data["abs_optimal_delta"] = ((data["bust_diff"] - 6.0).abs()).round(1)
    data["is_negative_ease"] = (data["bust_diff"] < 2.0).astype(int)

    # 2. Tỷ lệ nhân trắc học cơ thể (Anthropometric Proportions)
    data["bust_to_waist"] = (data["body_bust"] / (data["body_waist"] + 1e-6)).round(3)
    data["bust_to_hip"] = (data["body_bust"] / (data["body_hips"] + 1e-6)).round(3)
    data["waist_to_hip"] = (data["body_waist"] / (data["body_hips"] + 1e-6)).round(3)
    data["body_frame_index"] = (
        (data["body_bust"] + data["body_waist"] + data["body_hips"]) / (data["body_height"] + 1e-6)
    ).round(3)

    return data


def extract_fit_features_single(inputs: Dict[str, float]) -> Dict[str, float]:
    """Trích xuất đặc trưng cho một mẫu đơn lẻ dùng cho Backend API (Real-time).

    Args:
        inputs: Dictionary chứa các số đo thô của người và áo.

    Returns:
        Dictionary chứa đầy đủ 15 đặc trưng đã làm tròn.
    """
    body_bust = round(float(inputs["body_bust"]), 1)
    body_height = round(float(inputs["body_height"]), 1)
    body_hips = round(float(inputs["body_hips"]), 1)
    body_waist = round(float(inputs["body_waist"]), 1)
    garment_bust = round(float(inputs["garment_bust"]), 1)
    garment_length = round(float(inputs["garment_length"]), 1)

    bust_diff = round(garment_bust - body_bust, 1)

    return {
        "body_bust": body_bust,
        "body_height": body_height,
        "body_hips": body_hips,
        "body_waist": body_waist,
        "garment_bust": garment_bust,
        "garment_length": garment_length,
        "bust_diff": bust_diff,
        "ease_ratio": round(garment_bust / (body_bust + 1e-6), 3),
        "length_to_height": round(garment_length / (body_height + 1e-6), 3),
        "abs_optimal_delta": round(abs(bust_diff - 6.0), 1),
        "is_negative_ease": int(bust_diff < 2.0),
        "bust_to_waist": round(body_bust / (body_waist + 1e-6), 3),
        "bust_to_hip": round(body_bust / (body_hips + 1e-6), 3),
        "waist_to_hip": round(body_waist / (body_hips + 1e-6), 3),
        "body_frame_index": round((body_bust + body_waist + body_hips) / (body_height + 1e-6), 3),
    }
