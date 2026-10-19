"""Phân đoạn các vùng giải phẫu cơ thể người theo trục Y (Task FIT-04)."""

from typing import Dict, Any
import numpy as np
import trimesh

from shared.constants.body_regions import (
    ALL_REGIONS,
    REGION_SHOULDER,
    REGION_CHEST,
    REGION_WAIST,
    REGION_HIP,
)


def segment_body_regions(body_mesh: trimesh.Trimesh) -> Dict[str, Any]:
    """Phân đoạn các đỉnh của Mesh cơ thể thành 4 vùng giải phẫu chính: Vai, Ngực, Eo, Hông.

    Phương pháp: Chuẩn hóa chiều cao đứng dọc theo trục Y (Y-up) và chia tầng theo tỷ lệ nhân trắc.

    Args:
        body_mesh: Trimesh cơ thể người (đơn vị: mét, hệ trục Y-up).

    Returns:
        Dictionary chứa thông tin từng vùng:
        {
            "region_name": {
                "indices": np.ndarray,      # Chỉ số các đỉnh thuộc vùng
                "y_range": (y_low, y_high), # Khoảng tọa độ Y thực tế (mét)
                "count": int                # Số đỉnh thuộc vùng
            }
        }
    """
    vertices = body_mesh.vertices
    if len(vertices) == 0:
        return {r: {"indices": np.zeros(0, dtype=int), "count": 0} for r in ALL_REGIONS}

    y_vals = vertices[:, 1]
    y_min, y_max = float(np.min(y_vals)), float(np.max(y_vals))
    height = max(y_max - y_min, 1e-6)

    # Tỷ lệ chiều cao tương đối dọc theo thân trên
    # Vai: 0.78 - 0.92; Ngực: 0.64 - 0.78; Eo: 0.50 - 0.64; Hông: 0.38 - 0.50
    relative_y = (y_vals - y_min) / height

    region_defs = {
        REGION_SHOULDER: (0.78, 0.92),
        REGION_CHEST: (0.64, 0.78),
        REGION_WAIST: (0.50, 0.64),
        REGION_HIP: (0.38, 0.50),
    }

    result: Dict[str, Any] = {}
    for region_name, (r_low, r_high) in region_defs.items():
        mask = (relative_y >= r_low) & (relative_y < r_high)
        indices = np.where(mask)[0]
        y_low = y_min + r_low * height
        y_high = y_min + r_high * height

        result[region_name] = {
            "indices": indices,
            "y_range": (round(y_low, 3), round(y_high, 3)),
            "count": len(indices),
        }

    return result
