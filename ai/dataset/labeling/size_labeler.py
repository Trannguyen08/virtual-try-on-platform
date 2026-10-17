"""Size labeling module for Virtual Try-On Platform (Module M4).

Defines standard apparel sizing thresholds based on anthropometric body bust measurements
and assigns discrete categorical size targets (S, M, L, XL) to dataset samples.
"""

from typing import Dict, List, Union
import numpy as np
import pandas as pd

# ==============================================================================
# 1. SIZE SYSTEM CONSTANTS (SINGLE SOURCE OF TRUTH)
# ==============================================================================
SIZE_ORDER: List[str] = ["S", "M", "L", "XL"]

# Ngưỡng chu vi vòng ngực người (cm) theo chuẩn phân cỡ ISO / ASTM
# S: < 94.0 cm
# M: 94.0 cm <= bust < 104.0 cm
# L: 104.0 cm <= bust < 114.0 cm
# XL: >= 114.0 cm
BUST_THRESHOLDS: Dict[str, float] = {
    "S_UPPER": 94.0,
    "M_UPPER": 104.0,
    "L_UPPER": 114.0,
}


# ==============================================================================
# 2. CORE LABELING FUNCTIONS
# ==============================================================================
def get_size_from_bust(body_bust: float) -> str:
    """Xác định nhãn size (S, M, L, XL) dựa trên vòng ngực người (cm).

    Quy tắc phân loại:
    - S  : body_bust < 94.0 cm
    - M  : 94.0 cm <= body_bust < 104.0 cm
    - L  : 104.0 cm <= body_bust < 114.0 cm
    - XL : body_bust >= 114.0 cm

    Args:
        body_bust: Chu vi vòng ngực (cm).

    Returns:
        Ký hiệu size: 'S', 'M', 'L', hoặc 'XL'.
    """
    if pd.isna(body_bust) or not np.isfinite(body_bust):
        raise ValueError(f"Giá trị body_bust không hợp lệ: {body_bust}")

    if body_bust < BUST_THRESHOLDS["S_UPPER"]:
        return "S"
    elif body_bust < BUST_THRESHOLDS["M_UPPER"]:
        return "M"
    elif body_bust < BUST_THRESHOLDS["L_UPPER"]:
        return "L"
    else:
        return "XL"


def assign_size_labels(
    df: pd.DataFrame,
    bust_col: str = "body_bust",
    target_col: str = "size_label",
) -> pd.DataFrame:
    """Gán cột nhãn kích cỡ (size_label) vào DataFrame.

    Tạo bản sao độc lập (copy) của DataFrame để tuân thủ nguyên tắc không mutate dữ liệu thô.

    Args:
        df: DataFrame chứa số đo cơ thể.
        bust_col: Tên cột chu vi ngực người (mặc định 'body_bust').
        target_col: Tên cột nhãn mục tiêu sẽ tạo (mặc định 'size_label').

    Returns:
        DataFrame mới có thêm cột target_col.
    """
    if bust_col not in df.columns:
        raise KeyError(f"Không tìm thấy cột '{bust_col}' trong DataFrame.")

    df_out = df.copy()
    df_out[target_col] = df_out[bust_col].apply(get_size_from_bust)
    return df_out


def check_size_distribution(
    df: pd.DataFrame,
    target_col: str = "size_label",
    min_ratio: float = 0.10,
) -> Dict[str, Union[bool, Dict[str, float]]]:
    """Kiểm tra phân phối kích cỡ có đạt điều kiện TC-AI-01 hay không.

    Tiêu chí nghiệm thu (TC-AI-01):
    Mỗi lớp kích cỡ (S, M, L, XL) phải chiếm tối thiểu min_ratio (10%) tổng mẫu.

    Args:
        df: DataFrame đã được gán nhãn size.
        target_col: Tên cột kích cỡ.
        min_ratio: Tỷ lệ tối thiểu cho mỗi lớp (mặc định 0.10 tức 10%).

    Returns:
        Dict chứa trạng thái 'is_valid', 'ratios', và 'warnings'.
    """
    if target_col not in df.columns:
        raise KeyError(f"Cột '{target_col}' chưa tồn tại trong DataFrame.")

    total_samples = len(df)
    counts = df[target_col].value_counts()
    ratios = {size: float(counts.get(size, 0) / total_samples) for size in SIZE_ORDER}

    warnings = []
    is_valid = True
    for size, ratio in ratios.items():
        if ratio < min_ratio:
            is_valid = False
            warnings.append(
                f"Lớp '{size}' chỉ chiếm {ratio * 100:.2f}% (< {min_ratio * 100:.1f}%)"
            )

    return {
        "is_valid": is_valid,
        "counts": {size: int(counts.get(size, 0)) for size in SIZE_ORDER},
        "ratios": ratios,
        "warnings": warnings,
    }
