"""Xuất file heatmap.json chuẩn hóa theo JSON Schema contract cho Frontend (Task FIT-06).

Đáp ứng tiêu chuẩn nghiệm thu TC-FIT-06:
- Xuất file heatmap.json validate 100% theo JSON Schema contract.
- Số phần tử mảng distances bằng đúng số đỉnh của mesh áo (vertex_count).
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union


def validate_heatmap_schema(data: Dict[str, Any]) -> bool:
    """Kiểm tra tính hợp lệ của dữ liệu Heatmap theo đúng hợp đồng của dự án.

    Args:
        data: Dữ liệu dictionary cần kiểm tra.

    Returns:
        True nếu dữ liệu chuẩn hợp đồng, ngược lại raise ValueError.
    """
    required_keys = ["garment_id", "size", "vertex_count", "unit", "min_distance", "max_distance", "distances"]
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Thiếu trường bắt buộc trong heatmap contract: '{key}'")

    if not isinstance(data["distances"], list):
        raise ValueError("Trường 'distances' bắt buộc phải là một danh sách (list)")

    if len(data["distances"]) != data["vertex_count"]:
        raise ValueError(
            f"Số phần tử distances ({len(data['distances'])}) không khớp với vertex_count ({data['vertex_count']})"
        )

    if data["unit"] != "cm":
        raise ValueError(f"Đơn vị ngoại vi trong heatmap bắt buộc là 'cm', nhận được: '{data['unit']}'")

    return True


def export_heatmap_json(
    heatmap_data: Dict[str, Any],
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """Validate và xuất dữ liệu Heatmap ra chuỗi JSON hoặc file trên ổ đĩa.

    Args:
        heatmap_data: Dictionary dữ liệu sinh từ generate_heatmap_payload.
        output_path: Đường dẫn file lưu trữ (tùy chọn, ví dụ: 'data/outputs/heatmap.json').

    Returns:
        Chuỗi ký tự JSON hợp lệ.
    """
    validate_heatmap_schema(heatmap_data)
    json_str = json.dumps(heatmap_data, indent=2, ensure_ascii=False)

    if output_path is not None:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(json_str)

    return json_str
