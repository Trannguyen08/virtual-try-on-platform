"""
Module: garment.mesh.size_scaling
Task ID: GAR-04
Test Case ID: TC-GAR-04

Thuật toán co dãn Mesh theo kích cỡ chuẩn và kiểm định chu vi lát cắt (Slicing Verification).
Tiêu chí nghiệm thu: Độ lệch chu vi ngực đo trên mesh <= 1.0 cm so với bảng Size Chart.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import trimesh

from garment.size_chart.garment_loader import GarmentChart, SizeMeasurement
from garment.mesh.mesh_generator import GarmentMeshGenerator


class SizeScalingError(Exception):
    """Lỗi co dãn hoặc sai số kích thước vượt ngưỡng cho phép."""
    pass


class SizeScaler:
    """Xử lý co dãn mesh theo thông số Size Chart và kiểm định chu vi mặt cắt."""

    def __init__(self, generator: Optional[GarmentMeshGenerator] = None) -> None:
        self.generator = generator or GarmentMeshGenerator()

    @staticmethod
    def measure_slice_circumference_cm(
        mesh: trimesh.Trimesh,
        height_y: float,
        normal: Tuple[float, float, float] = (0.0, 1.0, 0.0),
    ) -> float:
        """
        Đo chu vi lát cắt ngang của mesh tại cao độ height_y (Đơn vị kết quả: cm).
        Cắt lát qua mặt phẳng Y = height_y, tách lấy vòng cung thân áo quanh gốc (X=0, Z=0).
        """
        plane_origin = np.array([0.0, height_y, 0.0], dtype=np.float64)
        plane_normal = np.array(normal, dtype=np.float64)

        section = mesh.section(plane_origin=plane_origin, plane_normal=plane_normal)
        if section is None:
            raise SizeScalingError(
                f"Mặt phẳng cắt tại Y={height_y:.3f}m không giao cắt với mesh."
            )

        # section là một Path3D trong Trimesh
        # Lọc các đường cong khép kín (discrete curves)
        discrete_paths = section.discrete
        if not discrete_paths:
            raise SizeScalingError(f"Không trích xuất được đường cong cắt lát tại Y={height_y:.3f}m")

        torso_length_m = 0.0
        # Tìm đường cong thân áo: có tâm X gần 0 nhất
        best_dist_to_center = float("inf")
        selected_path = None

        for path in discrete_paths:
            if len(path) < 3:
                continue
            centroid_x = float(np.mean(path[:, 0]))
            dist_to_center = abs(centroid_x)
            # Thân áo nằm ở vị trí trung tâm quanh X=0, ống tay nằm ở hai bên
            if dist_to_center < best_dist_to_center:
                best_dist_to_center = dist_to_center
                selected_path = path

        if selected_path is not None:
            diffs = np.diff(selected_path, axis=0)
            torso_length_m = float(np.sum(np.linalg.norm(diffs, axis=1)))
            # Nếu điểm đầu và điểm cuối chưa đóng kín
            close_dist = float(np.linalg.norm(selected_path[0] - selected_path[-1]))
            if close_dist > 1e-4:
                torso_length_m += close_dist
        else:
            # Fallback lấy tổng chiều dài toàn bộ section
            torso_length_m = float(section.length)

        return torso_length_m * 100.0

    def measure_chest_circumference_cm(
        self,
        mesh: trimesh.Trimesh,
        height_ratio: float = 0.70,
    ) -> float:
        """
        Đo chu vi ngực trên mesh tại vị trí tỷ lệ height_ratio (mặc định 70% từ gấu áo lên).
        """
        bounds = mesh.bounds
        y_min = float(bounds[0][1])
        y_max = float(bounds[1][1])
        chest_y = y_min + (y_max - y_min) * height_ratio
        return self.measure_slice_circumference_cm(mesh, height_y=chest_y)

    def verify_size_accuracy(
        self,
        mesh: trimesh.Trimesh,
        expected_chest_cm: float,
        tolerance_cm: float = 1.0,
        height_ratio: float = 0.70,
    ) -> Tuple[bool, float, float]:
        """
        Kiểm định độ chính xác kích thước chu vi ngực (TC-GAR-04):
        |C_measured - C_expected| <= tolerance_cm (mặc định 1.0 cm).
        Trả về: (is_passed, measured_cm, delta_cm)
        """
        measured_cm = self.measure_chest_circumference_cm(mesh, height_ratio=height_ratio)
        delta_cm = abs(measured_cm - expected_chest_cm)
        is_passed = delta_cm <= tolerance_cm
        return is_passed, measured_cm, delta_cm

    def scale_mesh(
        self,
        base_mesh: trimesh.Trimesh,
        base_spec: SizeMeasurement,
        target_spec: SizeMeasurement,
    ) -> trimesh.Trimesh:
        """
        Biến dạng co dãn (Morphing/Scaling) từ mesh base sang size mục tiêu.
        """
        # Nếu đã có generator, sinh trực tiếp theo target_spec đảm bảo giải tích chính xác nhất
        if self.generator:
            return self.generator.generate_tshirt(target_spec)

        # Fallback: Co dãn trực tiếp các đỉnh của base_mesh theo tỷ lệ 3 trục
        s_xz = target_spec.chest_m / base_spec.chest_m
        s_y = target_spec.length_m / base_spec.length_m
        s_x = target_spec.shoulder_width_m / base_spec.shoulder_width_m

        vertices = base_mesh.vertices.copy()
        y_min = float(np.min(vertices[:, 1]))
        y_max = float(np.max(vertices[:, 1]))
        h = max(y_max - y_min, 1e-4)

        for i in range(len(vertices)):
            vx, vy, vz = vertices[i]
            t = (vy - y_min) / h
            # Tỷ lệ co dãn X thay đổi dần từ ngực lên vai
            cur_sx = s_xz * (1.0 - t) + s_x * t
            vertices[i, 0] = vx * cur_sx
            vertices[i, 1] = y_min + (vy - y_min) * s_y
            vertices[i, 2] = vz * s_xz

        scaled_mesh = trimesh.Trimesh(
            vertices=vertices,
            faces=base_mesh.faces.copy(),
            process=True,
        )
        scaled_mesh.fix_normals()
        return scaled_mesh

    def generate_all_sizes(
        self,
        chart: GarmentChart,
        output_dir: Optional[Path | str] = None,
    ) -> Dict[str, trimesh.Trimesh]:
        """
        Sinh đồng loạt 4 file mesh tương ứng với 4 size S, M, L, XL.
        Kiểm định toàn bộ chu vi ngực lệch <= 1.0 cm.
        """
        results: Dict[str, trimesh.Trimesh] = {}
        for sz_name, spec in chart.sizes.items():
            mesh = self.generator.generate_tshirt(spec)
            passed, measured_cm, delta_cm = self.verify_size_accuracy(
                mesh, expected_chest_cm=spec.chest_cm, tolerance_cm=1.0
            )
            if not passed:
                raise SizeScalingError(
                    f"Size {sz_name} không đạt chuẩn TC-GAR-04: Đo được {measured_cm:.2f}cm, "
                    f"Kỳ vọng {spec.chest_cm:.2f}cm, Lệch {delta_cm:.2f}cm > 1.0cm"
                )

            results[sz_name] = mesh
            if output_dir:
                out_path = Path(output_dir) / f"{chart.category}_{sz_name.lower()}.obj"
                self.generator.export_mesh(mesh, out_path)

        return results
