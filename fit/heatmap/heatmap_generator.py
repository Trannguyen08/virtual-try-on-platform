"""Tạo dữ liệu Heatmap khoảng cách từng đỉnh (Task FIT-06).

Ánh xạ khoảng cách từ Mét (nội bộ) sang Centimet (ngoại vi theo hợp đồng M5)
kèm phân loại dải màu chuyển sắc (Vertex Colors).
"""

from typing import Any, Dict, Optional
import numpy as np


def generate_heatmap_payload(
    per_vertex_distance_m: np.ndarray,
    is_penetrating: Optional[np.ndarray] = None,
    garment_id: str = "garment_demo",
    size: str = "M",
) -> Dict[str, Any]:
    """Sinh cấu trúc dữ liệu Heatmap theo đúng hợp đồng với Frontend WebGL (M5).

    Args:
        per_vertex_distance_m: Mảng khoảng cách từng đỉnh (đơn vị: mét).
        is_penetrating: Mảng boolean đánh dấu đỉnh bị lẹm (nếu có, đổi thành khoảng cách âm).
        garment_id: Mã định danh mẫu áo.
        size: Kích cỡ áo (S, M, L, XL).

    Returns:
        Dictionary hợp đồng:
        {
            "garment_id": str,
            "size": str,
            "vertex_count": int,
            "unit": "cm",
            "min_distance": float,
            "max_distance": float,
            "distances": list[float]
        }
    """
    vertex_count = len(per_vertex_distance_m)
    if vertex_count == 0:
        return {
            "garment_id": garment_id,
            "size": size,
            "vertex_count": 0,
            "unit": "cm",
            "min_distance": 0.0,
            "max_distance": 0.0,
            "distances": [],
        }

    # Chuyển đổi từ mét sang centimet (1 m = 100 cm)
    distances_cm = per_vertex_distance_m * 100.0

    # Nếu có đỉnh xuyên thấu, gán dấu âm để thể hiện độ lẹm vào bên trong
    if is_penetrating is not None and len(is_penetrating) == vertex_count:
        distances_cm = np.where(is_penetrating, -distances_cm, distances_cm)

    # Làm tròn 2 chữ số thập phân
    distances_list = [round(float(d), 2) for d in distances_cm]

    min_d = round(float(np.min(distances_cm)), 2)
    max_d = round(float(np.max(distances_cm)), 2)

    return {
        "garment_id": garment_id,
        "size": size,
        "vertex_count": vertex_count,
        "unit": "cm",
        "min_distance": min_d,
        "max_distance": max_d,
        "distances": distances_list,
    }
