"""
Module: garment.mesh.pants_generator
Task ID: GAR-02 (Pants)
Test Case ID: TC-GAR-02

Bộ sinh mô hình 3D Parametric Mesh hoàn chỉnh cho Quần (True 3D Pants Manifold Geometry).
Cấu trúc hình học 3D gồm:
- Thân trên (Waist / Pelvis): Ống trụ elip 3D khép kín bao quanh hông từ cạp quần đến đũng quần.
- Hai ống chân (Left & Right Pant Legs): Hai ống trụ 3D khép kín độc lập từ đùi xuống mắt cá chân.
- Lỗ mở cạp quần (Waist Opening) và hai lỗ gấu quần (Ankle Cuffs) mở thực tế.
- Chuẩn hóa: Đơn vị Mét (m), Hệ trục Y-up, +Z forward, số đỉnh <= 30.000.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Optional, Tuple, Any

import numpy as np
import trimesh

from garment.size_chart.garment_loader import GarmentChart, SizeMeasurement
from garment.mesh.mesh_generator import _ellipse_semi_axes


class PantsMeshGenerator:
    """Sinh mô hình Quần 3D Parametric manifold thực thụ."""

    def __init__(self, ankle_y_offset: float = 0.08) -> None:
        """
        ankle_y_offset: Cao độ gấu quần (mắt cá chân) so với sàn (mặc định 0.08m khớp SMPL-X).
        """
        self.ankle_y_offset = ankle_y_offset

    def generate_pants(
        self,
        spec: SizeMeasurement,
        rings_pelvis: int = 16,
        rings_leg: int = 24,
        radial_resolution: int = 36,
        texture_image: Optional[Any] = None,
    ) -> trimesh.Trimesh:
        """
        Sinh mesh 3D Quần manifold hoàn chỉnh theo thông số số đo SizeMeasurement.
        """
        length = spec.length_m if spec.length_m > 0 else 1.00
        waist_circ = spec.waist_m if spec.waist_m > 0 else 0.80
        hip_circ = spec.hip_m if spec.hip_m > 0 else 0.98
        thigh_circ = spec.thigh_m if spec.thigh_m > 0 else 0.58
        hem_circ = spec.hem_m if spec.hem_m > 0 else 0.36

        # Bán trục các vùng chính
        a_waist, b_waist = _ellipse_semi_axes(waist_circ, width_to_depth_ratio=1.35)
        a_hip, b_hip = _ellipse_semi_axes(hip_circ, width_to_depth_ratio=1.32)

        # Bán kính đùi và gấu quần
        r_thigh = (thigh_circ / (2.0 * math.pi))
        r_hem = (hem_circ / (2.0 * math.pi))

        y_ankle = self.ankle_y_offset
        y_waist = y_ankle + length
        # Đũng quần nằm ở khoảng 74% chiều dài từ trên xuống (hoặc dựa trên inseam)
        inseam_len = spec.inseam_m if spec.inseam_m > 0 else (length * 0.73)
        y_crotch = y_ankle + inseam_len
        pelvis_height = max(y_waist - y_crotch, 0.15)
        leg_height = max(y_crotch - y_ankle, 0.50)

        all_vertices = []
        all_faces = []

        # ── 1. Thân trên: Phần Hông & Cạp quần (Pelvis Tube) ───────────────
        vertices_pelvis = []
        for i in range(rings_pelvis + 1):
            t = i / rings_pelvis  # 0.0 (crotch) -> 1.0 (waist)
            cur_y = y_crotch + t * pelvis_height

            # Nội suy từ đũng/hông lên cạp quần
            if t <= 0.60:
                k = t / 0.60
                cur_a = a_hip * (0.95 + 0.05 * k)
                cur_b = b_hip * (0.95 + 0.05 * k)
            else:
                k = (t - 0.60) / 0.40
                cur_a = a_hip + k * (a_waist - a_hip)
                cur_b = b_hip + k * (b_waist - b_hip)

            for j in range(radial_resolution):
                theta = 2.0 * math.pi * (j / radial_resolution)
                vx = cur_a * math.cos(theta)
                vy = cur_y
                vz = cur_b * math.sin(theta)
                vertices_pelvis.append([vx, vy, vz])

        faces_pelvis = []
        for i in range(rings_pelvis):
            for j in range(radial_resolution):
                next_j = (j + 1) % radial_resolution
                v0 = i * radial_resolution + j
                v1 = i * radial_resolution + next_j
                v2 = (i + 1) * radial_resolution + next_j
                v3 = (i + 1) * radial_resolution + j
                faces_pelvis.append([v0, v1, v2])
                faces_pelvis.append([v0, v2, v3])

        all_vertices.extend(vertices_pelvis)
        all_faces.extend(faces_pelvis)

        # ── 2. Hai Ống Chân (Left & Right Pant Legs) ───────────────────────
        leg_offset_x = a_hip * 0.48  # Khoảng cách từ tâm đến trọng tâm mỗi chân

        for side, sign in [("right", 1.0), ("left", -1.0)]:
            leg_center_x = sign * leg_offset_x
            v_offset = len(all_vertices)

            for i in range(rings_leg + 1):
                t = i / rings_leg  # 0.0 (ankle) -> 1.0 (crotch/thigh)
                cur_y = y_ankle + t * leg_height

                # Bán kính thu hẹp dần từ đùi xuống cổ chân
                cur_r = r_hem + t * (r_thigh - r_hem)
                # Nghiêng nhẹ ống chân vào phía trong tự nhiên
                cur_cx = leg_center_x * (0.92 + 0.08 * t)

                for j in range(radial_resolution):
                    theta = 2.0 * math.pi * (j / radial_resolution)
                    vx = cur_cx + cur_r * math.cos(theta)
                    vy = cur_y
                    vz = cur_r * math.sin(theta)
                    all_vertices.append([vx, vy, vz])

            for i in range(rings_leg):
                for j in range(radial_resolution):
                    next_j = (j + 1) % radial_resolution
                    v0 = v_offset + i * radial_resolution + j
                    v1 = v_offset + i * radial_resolution + next_j
                    v2 = v_offset + (i + 1) * radial_resolution + next_j
                    v3 = v_offset + (i + 1) * radial_resolution + j
                    if sign > 0:
                        all_faces.append([v0, v1, v2])
                        all_faces.append([v0, v2, v3])
                    else:
                        all_faces.append([v0, v2, v1])
                        all_faces.append([v0, v3, v2])

        # Xây dựng UV Coordinates
        uvs = []
        for v in all_vertices:
            vx, vy, vz = v
            u = 0.5 + 0.48 * (vx / max(a_hip, 1e-4))
            v_coord = (vy - y_ankle) / max(length, 1e-4)
            u = max(0.01, min(0.99, u))
            v_coord = max(0.01, min(0.99, v_coord))
            uvs.append([u, v_coord])

        mesh_vertices = np.array(all_vertices, dtype=np.float64)
        mesh_faces = np.array(all_faces, dtype=np.int64)
        mesh_uvs = np.array(uvs, dtype=np.float64)

        mesh = trimesh.Trimesh(vertices=mesh_vertices, faces=mesh_faces, process=True)
        mesh.fix_normals()

        # Gán Texture nếu có
        if texture_image is not None:
            try:
                from PIL import Image as PILImage
                if isinstance(texture_image, PILImage.Image):
                    img_rgb = texture_image.convert("RGB")
                    material = trimesh.visual.material.PBRMaterial(
                        baseColorTexture=img_rgb,
                        metallicFactor=0.0,
                        roughnessFactor=0.85,
                    )
                    mesh.visual = trimesh.visual.TextureVisuals(uv=mesh_uvs, material=material)
            except Exception:
                pass

        return mesh

    def generate_from_chart(
        self,
        chart: GarmentChart,
        size: str = "M",
        texture_image: Optional[Any] = None,
    ) -> trimesh.Trimesh:
        """Sinh mesh 3D Quần trực tiếp từ GarmentChart và Size."""
        spec = chart.get_size(size)
        return self.generate_pants(spec, texture_image=texture_image)

    @staticmethod
    def export_mesh(mesh: trimesh.Trimesh, output_path: Path | str) -> Path:
        """Xuất file 3D mesh sang định dạng .obj hoặc .glb."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        file_ext = out.suffix.lower()
        if file_ext == ".glb":
            out.write_bytes(mesh.export(file_type="glb"))
        else:
            out.write_bytes(mesh.export(file_type="obj").encode("utf-8"))
        return out
