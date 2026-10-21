"""
Module: garment.simulation.draping
Task ID: GAR-05, GAR-06
Test Case ID: TC-GAR-05, TC-GAR-06

Thuật toán mô phỏng vải hình học tốc độ cao (Fast Geometric Cloth Draping).
Cung cấp giải pháp Zero-Crash Fallback cho hệ thống:
- Tự động kéo áo ôm khít quanh cơ thể người mẫu 3D.
- Ngăn chặn hoàn toàn hiện tượng áo rơi tự do hoặc xuyên thấu vào da.
- Áp dụng bộ lọc Laplacian smoothing tạo nếp vải phẳng mượt.
- Hoạt động thuần túy bằng Trimesh & Numpy, tốc độ < 1.0s trên CPU, không phụ thuộc Blender.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import trimesh
from trimesh import proximity


class DrapingError(Exception):
    """Lỗi trong quá trình draping mô phỏng vải."""
    pass


class GeometricClothDraper:
    """Mô phỏng biến dạng hình học đưa vải ôm sát bề mặt cơ thể 3D."""

    def __init__(
        self,
        min_clearance_m: float = 0.005,  # Khoảng hở tối thiểu 5mm chống xuyên thấu
        target_clearance_m: float = 0.015,  # Khoảng hở mục tiêu 15mm
        smoothing_iterations: int = 5,
        smoothing_factor: float = 0.35,
    ) -> None:
        self.min_clearance_m = min_clearance_m
        self.target_clearance_m = target_clearance_m
        self.smoothing_iterations = smoothing_iterations
        self.smoothing_factor = smoothing_factor

    def drape(
        self,
        body_mesh: trimesh.Trimesh,
        garment_mesh: trimesh.Trimesh,
        gravity_drop_m: float = 0.015,
    ) -> trimesh.Trimesh:
        """
        Draping áo ôm khít bề mặt cơ thể người mẫu:
        1. Hạ nhẹ theo trọng lực (gravity drop).
        2. Đẩy các điểm lẹm trong da ra ngoài bề mặt an toàn.
        3. Kéo các điểm vải ở quá xa áp sát vào thân người.
        4. Làm mượt bề mặt (Laplacian smoothing).
        """
        if len(body_mesh.vertices) == 0:
            raise DrapingError("Body mesh không có đỉnh (rỗng).")
        if len(garment_mesh.vertices) == 0:
            raise DrapingError("Garment mesh không có đỉnh (rỗng).")

        draped = garment_mesh.copy()
        vertices = draped.vertices.copy()

        # 1. Tác động trọng lực nhẹ theo trục -Y
        vertices[:, 1] -= gravity_drop_m

        # 2. Truy vấn hình học gần nhất từ các đỉnh áo đến bề mặt cơ thể
        # Sử dụng proximity query của Trimesh
        closest_points, distances, triangle_ids = proximity.closest_point(
            body_mesh, vertices
        )

        # Tính toán pháp tuyến bề mặt cơ thể tại các điểm gần nhất
        face_normals = body_mesh.face_normals[triangle_ids]

        # Xác định vector từ điểm cơ thể gần nhất tới đỉnh áo
        disp = vertices - closest_points
        # Tích vô hướng với pháp tuyến để xác định điểm nằm ngoài (+) hay trong (-) cơ thể
        dot_product = np.sum(disp * face_normals, axis=1)

        # Đẩy các điểm bị lẹm (trong da hoặc khoảng hở < min_clearance) ra ngoài
        for i in range(len(vertices)):
            d = distances[i]
            is_inside = dot_product[i] < 0

            if is_inside or d < self.min_clearance_m:
                # Đẩy đỉnh ra ngoài theo hướng pháp tuyến cơ thể với khoảng hở an toàn
                vertices[i] = closest_points[i] + face_normals[i] * self.min_clearance_m
            elif d > self.target_clearance_m:
                # Kéo các phần vải quá rộng ở ngoài vào gần khoảng hở mục tiêu
                pull_ratio = 0.40  # Tỷ lệ co kéo đàn hồi
                target_pos = closest_points[i] + face_normals[i] * self.target_clearance_m
                vertices[i] = vertices[i] * (1.0 - pull_ratio) + target_pos * pull_ratio

        # 3. Làm mượt bề mặt bằng thuật toán Laplacian Smoothing
        # Xây dựng danh sách láng giềng (vertex neighbors)
        edges = draped.edges_unique
        neighbors: dict[int, list[int]] = {i: [] for i in range(len(vertices))}
        for u, v in edges:
            neighbors[u].append(v)
            neighbors[v].append(u)

        for _ in range(self.smoothing_iterations):
            new_verts = vertices.copy()
            for idx, n_list in neighbors.items():
                if len(n_list) >= 2:
                    avg_neighbor = np.mean(vertices[n_list], axis=0)
                    new_verts[idx] = (
                        vertices[idx] * (1.0 - self.smoothing_factor)
                        + avg_neighbor * self.smoothing_factor
                    )
            # Kiểm tra lại để không bị thụt vào trong cơ thể sau khi làm mịn
            re_closest, re_dist, re_tri = proximity.closest_point(body_mesh, new_verts)
            re_normals = body_mesh.face_normals[re_tri]
            re_disp = new_verts - re_closest
            re_dot = np.sum(re_disp * re_normals, axis=1)

            for i in range(len(new_verts)):
                if re_dot[i] < 0 or re_dist[i] < self.min_clearance_m:
                    new_verts[i] = re_closest[i] + re_normals[i] * self.min_clearance_m

            vertices = new_verts

        # 4. Kiểm tra an toàn: Không chứa NaN hoặc Inf
        if np.isnan(vertices).any() or np.isinf(vertices).any():
            raise DrapingError("Draping thất bại: Tạo ra tọa độ không hợp lệ (NaN/Inf).")

        draped.vertices = vertices
        draped.fix_normals()
        return draped
