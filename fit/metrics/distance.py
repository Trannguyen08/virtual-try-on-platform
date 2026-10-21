"""Tính toán khoảng cách bề mặt từng đỉnh (Distance) giữa Mesh áo và Mesh cơ thể (Task FIT-02).

Đáp ứng tiêu chuẩn nghiệm thu TC-FIT-02:
- Vỏ cầu áo cách bề mặt cơ thể đúng 2.0 cm: avg_distance ≈ 0.02 m (sai số <= 0.001 m).
- Mảng per_vertex_distance có độ dài đúng bằng tổng số đỉnh của mesh áo.
"""

from typing import Any, Dict
import numpy as np
import trimesh

from fit.utils.proximity import query_surface_proximity


def compute_distance(body_mesh: trimesh.Trimesh, garment_mesh: trimesh.Trimesh) -> Dict[str, Any]:
    """Tính khoảng cách từ mỗi đỉnh của mesh áo tới điểm gần nhất trên bề mặt cơ thể.

    Args:
        body_mesh: Trimesh đại diện cho cơ thể (đơn vị: mét).
        garment_mesh: Trimesh đại diện cho trang phục (đơn vị: mét).

    Returns:
        Dictionary chứa:
        - per_vertex_distance: Mảng khoảng cách từng đỉnh (numpy array, đơn vị: mét).
        - avg_distance: Khoảng cách trung bình (mét).
        - min_distance: Khoảng cách nhỏ nhất (mét).
        - max_distance: Khoảng cách lớn nhất (mét).
        - std_distance: Độ lệch chuẩn của khoảng cách (mét).
        - distance_score: Điểm khoảng cách chuẩn hóa thang 0 đến 100.
    """
    vertices = garment_mesh.vertices
    total_vertices = len(vertices)

    if total_vertices == 0:
        return {
            "per_vertex_distance": np.zeros(0, dtype=np.float32),
            "avg_distance": 0.0,
            "min_distance": 0.0,
            "max_distance": 0.0,
            "std_distance": 0.0,
            "distance_score": 0.0,
        }

    # Đo khoảng cách Euclid từ từng đỉnh tới bề mặt gần nhất thông qua Proximity Engine
    _, distances, _, _ = query_surface_proximity(body_mesh, vertices)
    per_vertex_distance = np.asarray(distances, dtype=np.float32)

    avg_d = float(np.mean(per_vertex_distance))
    min_d = float(np.min(per_vertex_distance))
    max_d = float(np.max(per_vertex_distance))
    std_d = float(np.std(per_vertex_distance))

    # Tính điểm Distance Score [0.0 - 100.0] dựa theo khoảng cách lý tưởng (0.015m - 0.025m = 1.5 - 2.5cm)
    optimal_center = 0.020  # 2.0 cm là điểm nới lý tưởng cho regular fit
    delta = abs(avg_d - optimal_center)

    if delta <= 0.005:  # Trong khoảng 1.5 - 2.5 cm -> Đạt điểm tối đa
        distance_score = 100.0
    elif avg_d < 0.015:  # Quá chật (dưới 1.5 cm)
        distance_score = max(0.0, 100.0 - (0.015 - avg_d) / 0.015 * 60.0)
    else:  # Quá rộng (trên 2.5 cm)
        distance_score = max(0.0, 100.0 - (avg_d - 0.025) / 0.040 * 100.0)

    return {
        "per_vertex_distance": per_vertex_distance,
        "avg_distance": round(avg_d, 4),
        "min_distance": round(min_d, 4),
        "max_distance": round(max_d, 4),
        "std_distance": round(std_d, 4),
        "distance_score": round(float(distance_score), 2),
    }
