"""Tính toán độ bao phủ giải phẫu (Coverage Ratio) của áo lên thân người (Task FIT-03).

Đáp ứng tiêu chuẩn nghiệm thu TC-FIT-03:
- Áo bao phủ 100% vùng torso: Coverage Ratio ≈ 1.0 (sai số <= 0.05).
- Áo bị cắt mất 50% diện tích bao phủ: Coverage Ratio ≈ 0.5 (sai số <= 0.05).
"""

from typing import Any, Dict, Optional
import numpy as np
import trimesh

from fit.utils.proximity import query_surface_proximity


def compute_coverage(
    body_mesh: trimesh.Trimesh,
    garment_mesh: trimesh.Trimesh,
    target_indices: Optional[np.ndarray] = None,
    max_threshold_distance: float = 0.08,
) -> Dict[str, Any]:
    """Tính toán tỷ lệ phần trăm diện tích hoặc số đỉnh cơ thể được che phủ bởi áo.

    Args:
        body_mesh: Trimesh đại diện cho cơ thể (đơn vị: mét).
        garment_mesh: Trimesh đại diện cho trang phục (đơn vị: mét).
        target_indices: Mảng chỉ số các đỉnh cơ thể mục tiêu (ví dụ: vùng torso).
                        Nếu None, mặc định lấy toàn bộ các đỉnh của body_mesh.
        max_threshold_distance: Khoảng cách tối đa để một điểm cơ thể được tính là
                                có vải che phủ phía ngoài (mặc định: 0.08 m = 8 cm).

    Returns:
        Dictionary chứa:
        - coverage_ratio: Tỷ lệ che phủ từ 0.0 đến 1.0.
        - coverage_score: Điểm bao phủ chuẩn hóa thang 0 đến 100.
        - covered_vertices: Số đỉnh cơ thể được che phủ.
        - total_target_vertices: Tổng số đỉnh cơ thể cần che phủ.
    """
    body_vertices = body_mesh.vertices
    if target_indices is not None and len(target_indices) > 0:
        target_vertices = body_vertices[target_indices]
    else:
        target_vertices = body_vertices

    total_target = len(target_vertices)
    if total_target == 0 or len(garment_mesh.vertices) == 0:
        return {
            "coverage_ratio": 0.0,
            "coverage_score": 0.0,
            "covered_vertices": 0,
            "total_target_vertices": total_target,
        }

    # Đo khoảng cách từ từng đỉnh cơ thể mục tiêu tới điểm gần nhất trên mặt áo
    _, distances, _, _ = query_surface_proximity(garment_mesh, target_vertices)
    is_covered = distances <= max_threshold_distance

    covered_count = int(np.sum(is_covered))
    coverage_ratio = float(covered_count / total_target)
    coverage_score = float(np.clip(100.0 * coverage_ratio, 0.0, 100.0))

    return {
        "coverage_ratio": round(coverage_ratio, 4),
        "coverage_score": round(coverage_score, 2),
        "covered_vertices": covered_count,
        "total_target_vertices": total_target,
        "is_covered": is_covered,
    }
