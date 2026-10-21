"""Phân loại độ vừa vặn tổng thể (Fit Classification) từ điểm Fit Score và trạng thái vùng."""

from typing import Dict, Any


def classify_overall_fit(
    fit_score: float,
    region_results: Dict[str, Any],
    penetration_ratio: float = 0.0,
) -> str:
    """Xác định nhãn phân loại độ vừa vặn tổng thể: Too Tight, Good, hoặc Too Loose.

    Args:
        fit_score: Điểm Fit Score tổng thể từ 0 đến 100.
        region_results: Kết quả đánh giá trạng thái 4 vùng cơ thể.
        penetration_ratio: Tỷ lệ xuyên thấu tổng thể.

    Returns:
        Chuỗi ký tự: 'Too Tight', 'Good', hoặc 'Too Loose'.
    """
    tight_regions = 0
    loose_regions = 0

    for _, info in region_results.items():
        st = info.get("status")
        if st == "TIGHT":
            tight_regions += 1
        elif st == "LOOSE":
            loose_regions += 1

    # 1. Nếu có tỷ lệ xuyên thấu hoặc các vùng chủ yếu bị chật -> Too Tight
    if tight_regions > loose_regions or penetration_ratio > 0.08:
        return "Too Tight"

    # 2. Nếu các vùng chủ yếu bị rộng -> Too Loose
    if loose_regions >= 2 and loose_regions > tight_regions:
        return "Too Loose"

    # 3. Phân loại theo điểm số tổng thể nếu các vùng cân bằng
    if fit_score >= 80.0 and tight_regions == 0 and loose_regions <= 1 and penetration_ratio <= 0.05:
        return "Good"
    elif loose_regions > 0:
        return "Too Loose"
    elif tight_regions > 0:
        return "Too Tight"

    return "Good" if fit_score >= 70.0 else "Too Tight"
