"""Công thức tính điểm Fit Score tổng thể từ các chỉ số hình học 3D (Task FIT-05).

Nguồn Chân lý Duy nhất (Single Source of Truth) cho trọng số và công thức điểm Fit của dự án.
Đáp ứng tiêu chuẩn nghiệm thu TC-FIT-05:
- Công thức: Fit Score = 0.4 * Penetration + 0.3 * Distance + 0.3 * Coverage
- Với Penetration = 95.0, Distance = 82.0, Coverage = 90.0 -> Fit Score = 89.6 (dung sai <= 0.05).
"""

from typing import Dict, Any

# Trọng số phê duyệt chính thức (Tổng = 1.0)
WEIGHT_PENETRATION: float = 0.4
WEIGHT_DISTANCE: float = 0.3
WEIGHT_COVERAGE: float = 0.3


def compute_fit_score(
    penetration_score: float,
    distance_score: float,
    coverage_score: float,
) -> float:
    """Tính điểm Fit Score tổng thể theo trọng số giải tích đã được phê duyệt.

    Args:
        penetration_score: Điểm xuyên thấu thang 0 đến 100 (Trọng số 40%).
        distance_score: Điểm khoảng cách bề mặt thang 0 đến 100 (Trọng số 30%).
        coverage_score: Điểm bao phủ giải phẫu thang 0 đến 100 (Trọng số 30%).

    Returns:
        Điểm Fit Score tổng thể từ 0.0 đến 100.0, làm tròn 2 chữ số thập phân.
    """
    score = (
        WEIGHT_PENETRATION * float(penetration_score)
        + WEIGHT_DISTANCE * float(distance_score)
        + WEIGHT_COVERAGE * float(coverage_score)
    )
    score_clamped = max(0.0, min(100.0, score))
    return round(score_clamped, 2)


def evaluate_fit_score_breakdown(
    penetration_metrics: Dict[str, Any],
    distance_metrics: Dict[str, Any],
    coverage_metrics: Dict[str, Any],
) -> Dict[str, Any]:
    """Tổng hợp chi tiết các thành phần điểm số và tính Fit Score cuối cùng.

    Args:
        penetration_metrics: Kết quả từ compute_penetration.
        distance_metrics: Kết quả từ compute_distance.
        coverage_metrics: Kết quả từ compute_coverage.

    Returns:
        Dictionary chứa điểm số tổng thể và điểm số chi tiết từng phần.
    """
    pen_score = float(penetration_metrics.get("penetration_score", 0.0))
    dist_score = float(distance_metrics.get("distance_score", 0.0))
    cov_score = float(coverage_metrics.get("coverage_score", 0.0))

    total_score = compute_fit_score(pen_score, dist_score, cov_score)

    return {
        "fit_score": total_score,
        "weights": {
            "penetration": WEIGHT_PENETRATION,
            "distance": WEIGHT_DISTANCE,
            "coverage": WEIGHT_COVERAGE,
        },
        "components": {
            "penetration_score": pen_score,
            "distance_score": dist_score,
            "coverage_score": cov_score,
        },
    }
