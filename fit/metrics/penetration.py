"""Tính toán tỷ lệ và độ sâu xuyên thấu (Penetration) giữa Mesh áo và Mesh cơ thể (Task FIT-01).

Đáp ứng tiêu chuẩn nghiệm thu TC-FIT-01:
- Áo nằm hoàn toàn ngoài cơ thể: Penetration Ratio = 0.0, Penetration Score = 100.0.
- Áo nhỏ hơn cơ thể (xuyên thấu hoàn toàn): Penetration Ratio = 1.0 (hoặc khớp giải tích toán học).
"""

from typing import Any, Dict
import numpy as np
import trimesh

from fit.utils.proximity import query_surface_proximity


def compute_penetration(body_mesh: trimesh.Trimesh, garment_mesh: trimesh.Trimesh) -> Dict[str, Any]:
    """Tính toán mức độ xuyên thấu của các đỉnh quần áo vào trong cơ thể.

    Args:
        body_mesh: Trimesh đại diện cho cơ thể (chuẩn hóa đơn vị mét).
        garment_mesh: Trimesh đại diện cho trang phục (chuẩn hóa đơn vị mét).

    Returns:
        Dictionary chứa:
        - penetration_ratio: Tỷ lệ đỉnh áo nằm bên trong cơ thể (từ 0.0 đến 1.0).
        - penetration_score: Điểm xuyên thấu thang 0 đến 100 (100 là hoàn toàn không xuyên).
        - max_penetration_depth: Độ lẹm sâu nhất đo được (đơn vị: mét).
        - num_penetrating: Số đỉnh bị xuyên thấu.
        - total_vertices: Tổng số đỉnh của mesh áo.
    """
    vertices = garment_mesh.vertices
    total_vertices = len(vertices)

    if total_vertices == 0:
        return {
            "penetration_ratio": 0.0,
            "penetration_score": 100.0,
            "max_penetration_depth": 0.0,
            "num_penetrating": 0,
            "total_vertices": 0,
            "is_penetrating": np.zeros(0, dtype=bool),
        }

    # Tính khoảng cách và xác định các điểm nằm bên trong cơ thể thông qua Proximity Engine
    _, distances, _, is_inside = query_surface_proximity(body_mesh, vertices)

    num_penetrating = int(np.sum(is_inside))
    penetration_ratio = float(num_penetrating / total_vertices)

    # Đo độ lẹm sâu nhất của các đỉnh nằm trong
    if num_penetrating > 0:
        max_penetration_depth = float(np.max(distances[is_inside]))
    else:
        max_penetration_depth = 0.0

    # Tính điểm số Penetration Score [0.0 - 100.0]
    penetration_score = float(np.clip(100.0 * (1.0 - penetration_ratio), 0.0, 100.0))

    return {
        "penetration_ratio": round(penetration_ratio, 4),
        "penetration_score": round(penetration_score, 2),
        "max_penetration_depth": round(max_penetration_depth, 4),
        "num_penetrating": num_penetrating,
        "total_vertices": total_vertices,
        "is_penetrating": is_inside,
    }
