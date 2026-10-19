"""
Module: garment.size_chart.garment_loader
Task ID: FND-09 / GAR-03
Test Case ID: TC-GAR-03

Bộ nạp và kiểm định bảng thông số kích thước (Size Chart Loader).
Đảm bảo tính hợp lệ, đơn vị chuẩn và tính đơn điệu tăng dần: S < M < L < XL.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


class SizeChartError(Exception):
    """Lỗi cấu hình bảng size chart hoặc vi phạm quy tắc đơn điệu."""
    pass


@dataclass(frozen=True)
class SizeMeasurement:
    """Số đo của một size trang phục cụ thể."""
    size: str
    chest_cm: float = 0.0
    waist_cm: float = 0.0
    hem_cm: float = 0.0
    shoulder_width_cm: float = 0.0
    length_cm: float = 0.0
    sleeve_length_cm: float = 0.0
    hip_cm: float = 0.0
    thigh_cm: float = 0.0
    inseam_cm: float = 0.0

    # Chuyển đổi sang đơn vị mét (chuẩn nội bộ)
    @property
    def chest_m(self) -> float:
        return self.chest_cm / 100.0

    @property
    def waist_m(self) -> float:
        return self.waist_cm / 100.0

    @property
    def hem_m(self) -> float:
        return self.hem_cm / 100.0

    @property
    def shoulder_width_m(self) -> float:
        return self.shoulder_width_cm / 100.0

    @property
    def length_m(self) -> float:
        return self.length_cm / 100.0

    @property
    def sleeve_length_m(self) -> float:
        return self.sleeve_length_cm / 100.0

    @property
    def hip_m(self) -> float:
        return self.hip_cm / 100.0

    @property
    def thigh_m(self) -> float:
        return self.thigh_cm / 100.0

    @property
    def inseam_m(self) -> float:
        return self.inseam_cm / 100.0


@dataclass
class GarmentChart:
    """Toàn bộ thông số bảng size của một loại trang phục."""
    category: str
    name: str
    sizes: Dict[str, SizeMeasurement]

    def get_size(self, size: str) -> SizeMeasurement:
        key = size.upper().strip()
        if key not in self.sizes:
            available = list(self.sizes.keys())
            raise SizeChartError(
                f"Size '{size}' không tồn tại trong bảng size (Hỗ trợ: {available})"
            )
        return self.sizes[key]


class GarmentLoader:
    """Trình nạp và kiểm định Size Chart cho trang phục 3D."""

    STANDARD_ORDER = ["S", "M", "L", "XL"]
    DEFAULT_CHARTS_DIR = Path(__file__).parent / "charts"

    def __init__(self, charts_dir: Optional[Path] = None) -> None:
        self.charts_dir = Path(charts_dir) if charts_dir else self.DEFAULT_CHARTS_DIR

    def load_from_dict(self, data: Dict[str, Any]) -> GarmentChart:
        """Nạp và kiểm định từ dictionary."""
        category = str(data.get("category", "custom")).lower()
        name = str(data.get("name", category))
        raw_sizes = data.get("sizes", {})

        if not raw_sizes:
            raise SizeChartError(f"Bảng size cho '{category}' rỗng (không có sizes).")

        parsed_sizes: Dict[str, SizeMeasurement] = {}

        # Hỗ trợ cả định dạng dict { "S": {...} } và list [ {"size": "S", ...} ]
        items_iterator = raw_sizes if isinstance(raw_sizes, list) else [
            {"size": sz, **item} for sz, item in raw_sizes.items()
        ]

        for item in items_iterator:
            sz = str(item.get("size", "")).upper()
            parsed_sizes[sz] = SizeMeasurement(
                size=sz,
                chest_cm=float(item.get("chest_cm", 0.0)),
                waist_cm=float(item.get("waist_cm", 0.0)),
                hem_cm=float(item.get("hem_cm", 0.0)),
                shoulder_width_cm=float(item.get("shoulder_width_cm", 0.0)),
                length_cm=float(item.get("length_cm", 0.0)),
                sleeve_length_cm=float(item.get("sleeve_length_cm", 0.0)),
                hip_cm=float(item.get("hip_cm", 0.0)),
                thigh_cm=float(item.get("thigh_cm", 0.0)),
                inseam_cm=float(item.get("inseam_cm", 0.0)),
            )

        # Kiểm định tính đơn điệu tăng dần bắt buộc: S < M < L < XL
        self._validate_monotonicity(parsed_sizes, category=category)

        return GarmentChart(category=category, name=name, sizes=parsed_sizes)

    def load_from_file(self, file_path: Path | str) -> GarmentChart:
        """Nạp từ đường dẫn file JSON cụ thể."""
        p = Path(file_path)
        if not p.is_file():
            raise FileNotFoundError(f"Không tìm thấy file size chart: {p}")
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise SizeChartError(f"File JSON không hợp lệ: {p} ({e})")
        return self.load_from_dict(data)

    def load_category(self, category: str) -> GarmentChart:
        """Nạp size chart theo tên danh mục (ví dụ 'tshirt', 'shirt', 'pants')."""
        cat_clean = category.lower().replace("-", "").replace("_", "")
        # Tìm file phù hợp
        candidates = [
            self.charts_dir / f"{cat_clean}.json",
            self.charts_dir / f"{category.lower()}.json",
        ]
        if cat_clean == "tshirt":
            candidates.append(self.charts_dir / "tshirt.json")
        elif cat_clean == "pants":
            candidates.append(self.charts_dir / "pants.json")

        for c in candidates:
            if c.is_file():
                return self.load_from_file(c)

        raise FileNotFoundError(
            f"Không tìm thấy file size chart cho danh mục '{category}' trong '{self.charts_dir}'"
        )

    def _validate_monotonicity(
        self, sizes: Dict[str, SizeMeasurement], category: str = "tshirt"
    ) -> None:
        """
        Kiểm định tính đơn điệu tăng dần nghiêm ngặt (TC-GAR-03):
        S < M < L < XL đối với các thông số đo chính.
        """
        keys_present = [k for k in self.STANDARD_ORDER if k in sizes]
        if len(keys_present) < 2:
            return  # Không đủ cặp để so sánh

        for i in range(len(keys_present) - 1):
            prev_key = keys_present[i]
            next_key = keys_present[i + 1]
            prev_m = sizes[prev_key]
            next_m = sizes[next_key]

            if category == "pants":
                # Kiểm tra eo
                if prev_m.waist_cm >= next_m.waist_cm:
                    raise SizeChartError(
                        f"Vi phạm tính đơn điệu eo quần: {prev_key} ({prev_m.waist_cm}cm) >= {next_key} ({next_m.waist_cm}cm)"
                    )
                # Kiểm tra hông
                if prev_m.hip_cm >= next_m.hip_cm:
                    raise SizeChartError(
                        f"Vi phạm tính đơn điệu hông quần: {prev_key} ({prev_m.hip_cm}cm) >= {next_key} ({next_m.hip_cm}cm)"
                    )
                # Kiểm tra dài quần
                if prev_m.length_cm >= next_m.length_cm:
                    raise SizeChartError(
                        f"Vi phạm tính đơn điệu dài quần: {prev_key} ({prev_m.length_cm}cm) >= {next_key} ({next_m.length_cm}cm)"
                    )
            else:
                # Kiểm tra ngực
                if prev_m.chest_cm >= next_m.chest_cm:
                    raise SizeChartError(
                        f"Vi phạm tính đơn điệu ngực: {prev_key} ({prev_m.chest_cm}cm) >= {next_key} ({next_m.chest_cm}cm)"
                    )
                # Kiểm tra dài áo
                if prev_m.length_cm >= next_m.length_cm:
                    raise SizeChartError(
                        f"Vi phạm tính đơn điệu dài áo: {prev_key} ({prev_m.length_cm}cm) >= {next_key} ({next_m.length_cm}cm)"
                    )
                # Kiểm tra rộng vai
                if prev_m.shoulder_width_cm >= next_m.shoulder_width_cm:
                    raise SizeChartError(
                        f"Vi phạm tính đơn điệu vai áo: {prev_key} ({prev_m.shoulder_width_cm}cm) >= {next_key} ({next_m.shoulder_width_cm}cm)"
                    )

