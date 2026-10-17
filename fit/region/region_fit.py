"""Đánh giá độ vừa vặn từng vùng giải phẫu: Ngực, Eo, Vai, Hông (Task FIT-04).

Đáp ứng tiêu chuẩn nghiệm thu TC-FIT-04:
- Phân loại chính xác từng vùng thuộc tập nhãn: {TIGHT, GOOD, LOOSE} theo đúng ngưỡng:
  + TIGHT: Khoảng cách < 0.5 cm (0.005 m) hoặc có tỷ lệ xuyên thấu cao.
  + GOOD:  0.5 cm <= Khoảng cách <= 3.0 cm (0.005 m <= d <= 0.030 m).
  + LOOSE: Khoảng cách > 3.0 cm (0.030 m).
"""

from typing import Any, Dict, Optional
import numpy as np
import trimesh

from shared.constants.body_regions import (
    ALL_REGIONS,
    STATUS_TIGHT,
    STATUS_GOOD,
    STATUS_LOOSE,
    THRESHOLD_TIGHT_MAX_M,
    THRESHOLD_GOOD_MAX_M,
)
from shared.constants.units import to_cm
from fit.region.body_regions import segment_body_regions
from fit.utils.proximity import query_surface_proximity


def evaluate_region_fit(
    body_mesh: trimesh.Trimesh,
    garment_mesh: trimesh.Trimesh,
    per_vertex_distance: Optional[np.ndarray] = None,
    is_penetrating: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """Phân loại độ vừa vặn chi tiết cho từng vùng cơ thể (Vai, Ngực, Eo, Hông).

    Phương pháp:
    1. Chiếu từng đỉnh của mesh áo tới điểm gần nhất trên bề mặt cơ thể.
    2. Điểm cơ thể gần nhất thuộc vùng nào thì đỉnh áo sẽ đại diện cho vùng đó.
    3. Tính khoảng cách trung bình của các đỉnh áo trong từng vùng và gán nhãn theo ngưỡng.

    Args:
        body_mesh: Trimesh cơ thể (đơn vị: mét, hệ trục Y-up).
        garment_mesh: Trimesh áo (đơn vị: mét, hệ trục Y-up).
        per_vertex_distance: Mảng khoảng cách từng đỉnh áo (tùy chọn, tính tự động nếu None).
        is_penetrating: Mảng boolean đánh dấu đỉnh áo bị lẹm vào cơ thể (tùy chọn).

    Returns:
        Dictionary chứa kết quả đánh giá cho từng vùng:
        {
            "chest": {"status": "GOOD", "avg_distance_cm": 1.8, "avg_distance_m": 0.018, ...},
            "waist": {"status": "TIGHT", ...}, ...
        }
    """
    vertices = garment_mesh.vertices
    if len(vertices) == 0:
        return {
            r: {"status": STATUS_GOOD, "avg_distance_cm": 0.0, "avg_distance_m": 0.0, "count": 0}
            for r in ALL_REGIONS
        }

    # 1. Tìm điểm gần nhất trên body và đo khoảng cách nếu chưa có thông qua Proximity Engine
    if per_vertex_distance is None or is_penetrating is None:
        closest_points, distances, _, is_inside = query_surface_proximity(body_mesh, vertices)
        if per_vertex_distance is None:
            per_vertex_distance = np.asarray(distances, dtype=np.float32)
        if is_penetrating is None:
            is_penetrating = is_inside
    else:
        closest_points, _, _, _ = query_surface_proximity(body_mesh, vertices)

    # 2. Phân đoạn vùng cơ thể để lấy ranh giới tọa độ Y
    body_regions = segment_body_regions(body_mesh)

    # 3. Phân loại từng đỉnh áo vào vùng cơ thể dựa trên tọa độ Y của điểm tiếp xúc trên body
    closest_y = closest_points[:, 1]
    results: Dict[str, Any] = {}

    for region_name in ALL_REGIONS:
        r_info = body_regions.get(region_name, {})
        y_low, y_high = r_info.get("y_range", (-np.inf, np.inf))

        # Mặt nạ các đỉnh áo thuộc vùng này
        in_region = (closest_y >= y_low) & (closest_y < y_high)
        region_count = int(np.sum(in_region))

        if region_count == 0:
            results[region_name] = {
                "status": STATUS_GOOD,
                "avg_distance_cm": 0.0,
                "avg_distance_m": 0.0,
                "count": 0,
                "penetration_ratio": 0.0,
            }
            continue

        region_dists = per_vertex_distance[in_region]
        avg_d_m = float(np.mean(region_dists))
        avg_d_cm = to_cm(avg_d_m)

        # Tính tỷ lệ xuyên thấu trong vùng
        if is_penetrating is not None:
            region_penetrations = is_penetrating[in_region]
            pen_ratio = float(np.mean(region_penetrations))
        else:
            pen_ratio = 0.0

        # Phân loại nhãn theo ngưỡng đã được phê duyệt
        if avg_d_m < THRESHOLD_TIGHT_MAX_M or pen_ratio > 0.15:
            status = STATUS_TIGHT
        elif avg_d_m <= THRESHOLD_GOOD_MAX_M:
            status = STATUS_GOOD
        else:
            status = STATUS_LOOSE

        results[region_name] = {
            "status": status,
            "avg_distance_cm": avg_d_cm,
            "avg_distance_m": round(avg_d_m, 4),
            "count": region_count,
            "penetration_ratio": round(pen_ratio, 3),
        }

    return results
