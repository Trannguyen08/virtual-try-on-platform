"""Fit labeling and feature engineering module for Virtual Try-On Platform (Module M4).

Defines interaction metrics between body measurements and garment dimensions (ease / delta),
assigns categorical fit classes ('Too Tight', 'Good', 'Too Loose'), and computes continuous
ground-truth Fit Score [0, 100] for AI model training and evaluation (Task AI-03).
"""

from typing import Dict, List, Union
import numpy as np
import pandas as pd

# ==============================================================================
# 1. FIT SYSTEM CONSTANTS (SINGLE SOURCE OF TRUTH)
# ==============================================================================
FIT_CLASSES: List[str] = ["Too Tight", "Good", "Too Loose"]

# Ngưỡng độ chênh lệch chu vi ngực (garment_bust - body_bust) tính bằng cm:
# - Quá chật (Too Tight): Chênh lệch < 2.0 cm (áo bó sát, căng kéo hoặc nhỏ hơn người)
# - Vừa vặn (Good): 2.0 cm <= Chênh lệch <= 12.0 cm (độ cử động chuẩn cho regular T-shirt)
# - Quá rộng (Too Loose): Chênh lệch > 12.0 cm (áo thụng, vai xệ, quá cỡ)
FIT_THRESHOLDS: Dict[str, float] = {
    "TIGHT_UPPER": 2.0,
    "GOOD_UPPER": 12.0,
    "OPTIMAL_EASE": 6.0,  # Độ chênh lệch lý tưởng nhất (điểm 100)
}


# ==============================================================================
# 2. CORE LABELING FUNCTIONS
# ==============================================================================
def get_fit_class_from_ease(bust_diff: float) -> str:
    """Xác định nhãn độ vừa (Too Tight, Good, Too Loose) dựa trên độ chênh ngực (cm).

    Args:
        bust_diff: garment_bust - body_bust (cm).

    Returns:
        Nhãn phân loại: 'Too Tight', 'Good', hoặc 'Too Loose'.
    """
    if pd.isna(bust_diff) or not np.isfinite(bust_diff):
        raise ValueError(f"Giá trị bust_diff không hợp lệ: {bust_diff}")

    if bust_diff < FIT_THRESHOLDS["TIGHT_UPPER"]:
        return "Too Tight"
    elif bust_diff <= FIT_THRESHOLDS["GOOD_UPPER"]:
        return "Good"
    else:
        return "Too Loose"


def compute_reference_fit_score(bust_diff: float) -> float:
    """Tính điểm Fit Score tham chiếu trong đoạn [0, 100] dựa trên độ chênh ngực.

    Công thức:
    - Điểm đạt tối đa 100 khi bust_diff = OPTIMAL_EASE (6.0 cm).
    - Khi bust_diff < 6.0 cm: Điểm giảm tuyến tính / bậc hai về 0 khi bị ép chặt (xuyên thấu).
    - Khi bust_diff > 6.0 cm: Điểm giảm dần theo độ rộng thùng thình, chặn dưới ở mức 30.

    Args:
        bust_diff: garment_bust - body_bust (cm).

    Returns:
        Điểm số fit trong khoảng [0.0, 100.0].
    """
    if pd.isna(bust_diff) or not np.isfinite(bust_diff):
        raise ValueError(f"Giá trị bust_diff không hợp lệ: {bust_diff}")

    optimal = FIT_THRESHOLDS["OPTIMAL_EASE"]
    delta = bust_diff - optimal

    if delta <= 0:
        # Áo chật hơn mức tối ưu (nguy cơ bó sát / xuyên thấu cao)
        # Giảm nhanh: nếu delta = -6 (tức bust_diff = 0), điểm = 70.
        # Nếu delta = -10 (bust_diff = -4), điểm = 40. Nếu delta <= -16, điểm = 0.
        score = 100.0 + (delta * 6.0)
    else:
        # Áo rộng hơn mức tối ưu (thụng nhưng không gây đau đớn / xuyên thấu vật lý)
        # Giảm từ từ: delta = +10 (bust_diff = 16), điểm = 75. delta = +20, điểm = 55.
        score = 100.0 - (delta * 2.2)

    return float(np.clip(score, 0.0, 100.0))


def assign_fit_labels(
    df: pd.DataFrame,
    body_bust_col: str = "body_bust",
    garment_bust_col: str = "garment_bust",
    class_target_col: str = "fit_class",
    score_target_col: str = "fit_score",
    diff_col: str = "bust_diff",
) -> pd.DataFrame:
    """Gán nhãn Fit Class, Fit Score và đặc trưng chênh lệch cho DataFrame.

    Args:
        df: DataFrame chứa các cột số đo body và garment.
        body_bust_col: Tên cột vòng ngực người (cm).
        garment_bust_col: Tên cột vòng ngực áo (cm).
        class_target_col: Tên cột nhãn phân loại đầu ra.
        score_target_col: Tên cột điểm fit số thực đầu ra.
        diff_col: Tên cột đặc trưng chênh lệch đầu ra.

    Returns:
        DataFrame mới đã bổ sung các cột nhãn và đặc trưng fit.
    """
    required_cols = [body_bust_col, garment_bust_col]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Thiếu các cột bắt buộc trong DataFrame: {missing}")

    result_df = df.copy()

    # 1. Tính đặc trưng tương tác: bust_diff = garment_bust - body_bust
    result_df[diff_col] = result_df[garment_bust_col] - result_df[body_bust_col]

    # 2. Gán nhãn phân loại (Fit Class)
    result_df[class_target_col] = result_df[diff_col].apply(get_fit_class_from_ease)

    # 3. Gán nhãn hồi quy (Fit Score)
    result_df[score_target_col] = result_df[diff_col].apply(compute_reference_fit_score)

    return result_df
