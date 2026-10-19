"""
Module: garment.mesh.mesh_generator
Task ID: GAR-02
Test Case ID: TC-GAR-02

Bộ sinh mô hình 3D Parametric Mesh hoàn chỉnh (True 3D Manifold Geometry).
Khác biệt hoàn toàn với mô hình 2.5D dẹt:
- Thân áo (Torso) dạng ống elip 3D khép kín trước-sau quanh cơ thể.
- Hai ống tay (Sleeves) là ống trụ 3D trái/phải vát nghiêng tự nhiên từ vai.
- Cổ áo (Neck hole) và gấu áo (Hem) mở thực tế.
- Chuẩn hóa: Đơn vị Mét (m), Hệ trục Y-up, +Z forward, số đỉnh <= 30.000.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import trimesh

from garment.size_chart.garment_loader import GarmentChart, SizeMeasurement


def _ellipse_semi_axes(circumference_m: float, width_to_depth_ratio: float = 1.35) -> Tuple[float, float]:
    """
    Tính bán trục a (nửa rộng X) và b (nửa sâu Z) của hình elip từ chu vi C
    dựa trên xấp xỉ Ramanujan: C ≈ π * [3(a+b) - sqrt((3a+b)(a+3b))]
    """
    r = width_to_depth_ratio
    # Với a = r * b, C = b * π * [3(r+1) - sqrt((3r+1)(r+3))]
    factor = math.pi * (3.0 * (r + 1.0) - math.sqrt((3.0 * r + 1.0) * (r + 3.0)))
    b = circumference_m / factor
    a = r * b
    return a, b


class GarmentMeshGenerator:
    """Sinh mô hình trang phục 3D Parametric dạng ống manifold thực thụ."""

    def __init__(self, base_y_offset: float = 0.90) -> None:
        """
        base_y_offset: Cao độ gấu áo (Hem) so với mặt đất (mặc định 0.90m khớp với thân dưới SMPL-X).
        """
        self.base_y_offset = base_y_offset

    def generate_tshirt(
        self,
        spec: SizeMeasurement,
        resolution_rings: int = 36,
        resolution_radial: int = 48,
        texture_image: Optional[Any] = None,
    ) -> trimesh.Trimesh:
        """
        Sinh mesh 3D T-Shirt manifold hoàn chỉnh theo thông số số đo (SizeMeasurement).
        """
        length = spec.length_m
        chest_circ = spec.chest_m
        waist_circ = spec.waist_m
        hem_circ = spec.hem_m
        shoulder_width = spec.shoulder_width_m
        sleeve_len = max(spec.sleeve_length_m, 0.20)

        # Bán trục các vòng chính
        a_hem, b_hem = _ellipse_semi_axes(hem_circ, width_to_depth_ratio=1.30)
        a_waist, b_waist = _ellipse_semi_axes(waist_circ, width_to_depth_ratio=1.32)
        a_chest, b_chest = _ellipse_semi_axes(chest_circ, width_to_depth_ratio=1.36)
        a_shoulder = shoulder_width / 2.0
        b_shoulder = b_chest * 0.92

        y_bottom = self.base_y_offset
        y_top = y_bottom + length

        # Phân đoạn độ cao thân áo
        # y: 0.0 -> Hem (Gấu áo)
        # y: 0.35 -> Waist (Vòng eo)
        # y: 0.70 -> Chest / Armpit (Ngực / Nách)
        # y: 0.90 -> Shoulder (Vai)
        # y: 1.00 -> Neck (Cổ áo)

        vertices_torso = []
        # Sinh lưới thân áo theo các vòng từ gấu lên vai
        for i in range(resolution_rings + 1):
            t = i / resolution_rings  # 0.0 -> 1.0
            cur_y = y_bottom + t * length

            if t <= 0.35:
                # Từ hem lên waist
                k = t / 0.35
                cur_a = a_hem + k * (a_waist - a_hem)
                cur_b = b_hem + k * (b_waist - b_hem)
            elif t <= 0.70:
                # Từ waist lên chest
                k = (t - 0.35) / 0.35
                cur_a = a_waist + k * (a_chest - a_waist)
                cur_b = b_waist + k * (b_chest - b_waist)
            elif t <= 0.92:
                # Từ chest lên shoulder seam
                k = (t - 0.70) / 0.22
                cur_a = a_chest + k * (a_shoulder - a_chest)
                cur_b = b_chest + k * (b_shoulder - b_chest)
            else:
                # Thu hẹp về phía chân cổ áo (Collar opening)
                k = (t - 0.92) / 0.08
                neck_radius_x = 0.09
                neck_radius_z = 0.08
                cur_a = a_shoulder + k * (neck_radius_x - a_shoulder)
                cur_b = b_shoulder + k * (neck_radius_z - b_shoulder)

            for j in range(resolution_radial):
                angle = 2.0 * math.pi * (j / resolution_radial)
                vx = cur_a * math.cos(angle)
                vz = cur_b * math.sin(angle)
                vy = cur_y
                # Hạ nhẹ cổ áo phía trước (+Z) tạo dáng cổ tròn tự nhiên
                if t > 0.85 and vz > 0:
                    scoop = (t - 0.85) / 0.15 * 0.035 * (vz / cur_b)
                    vy -= scoop
                vertices_torso.append([vx, vy, vz])

        # Tạo faces cho thân áo dạng ống trụ elip khép kín
        faces_torso = []
        for i in range(resolution_rings):
            for j in range(resolution_radial):
                next_j = (j + 1) % resolution_radial
                v0 = i * resolution_radial + j
                v1 = i * resolution_radial + next_j
                v2 = (i + 1) * resolution_radial + next_j
                v3 = (i + 1) * resolution_radial + j
                # 2 tam giác cho mỗi quad (đảm bảo pháp tuyến hướng ra ngoài)
                faces_torso.append([v0, v1, v2])
                faces_torso.append([v0, v2, v3])

        all_vertices = list(vertices_torso)
        all_faces = list(faces_torso)

        # Ống tay áo 3D (Left & Right Sleeves)
        arm_y = y_bottom + length * 0.78
        arm_radius = 0.095  # Chu vi ống tay ~ 60cm
        sleeve_rings = 14
        sleeve_radial = 24
        sleeve_angle = math.radians(28.0)  # Vát nghiêng 28 độ xuống dưới

        for side, sign in [("right", 1.0), ("left", -1.0)]:
            shoulder_anchor_x = sign * (a_shoulder * 0.95)
            sleeve_v_offset = len(all_vertices)

            for sr in range(sleeve_rings + 1):
                st = sr / sleeve_rings
                dist = st * sleeve_len
                # Tâm ống tay tại bước sr
                cx = shoulder_anchor_x + sign * dist * math.cos(sleeve_angle)
                cy = arm_y - dist * math.sin(sleeve_angle)
                # Bán kính ống tay thu nhỏ nhẹ về phía cổ tay
                cur_r = arm_radius * (1.0 - 0.12 * st)

                for sj in range(sleeve_radial):
                    theta = 2.0 * math.pi * (sj / sleeve_radial)
                    # Tiết diện vuông góc với hướng ống tay
                    dx = 0.0
                    dy = cur_r * math.cos(theta) * math.cos(sleeve_angle)
                    dz = cur_r * math.sin(theta)
                    vx = cx + dx
                    vy = cy + dy
                    vz = dz
                    all_vertices.append([vx, vy, vz])

            for sr in range(sleeve_rings):
                for sj in range(sleeve_radial):
                    next_sj = (sj + 1) % sleeve_radial
                    v0 = sleeve_v_offset + sr * sleeve_radial + sj
                    v1 = sleeve_v_offset + sr * sleeve_radial + next_sj
                    v2 = sleeve_v_offset + (sr + 1) * sleeve_radial + next_sj
                    v3 = sleeve_v_offset + (sr + 1) * sleeve_radial + sj
                    if sign > 0:
                        all_faces.append([v0, v1, v2])
                        all_faces.append([v0, v2, v3])
                    else:
                        all_faces.append([v0, v2, v1])
                        all_faces.append([v0, v3, v2])

        # Xây dựng UV coordinates
        uvs = []
        # UV cho thân áo: trải chiếu đều từ trước ra sau
        for v in all_vertices[:len(vertices_torso)]:
            vx, vy, vz = v
            # Chiếu theo trục X và Y
            u = 0.5 + 0.48 * (vx / max(a_shoulder, 1e-4))
            v_coord = (vy - y_bottom) / max(length, 1e-4)
            u = max(0.01, min(0.99, u))
            v_coord = max(0.01, min(0.99, v_coord))
            uvs.append([u, v_coord])

        # UV cho ống tay áo
        max_arm_span = a_shoulder + sleeve_len
        for v in all_vertices[len(vertices_torso):]:
            vx, vy, vz = v
            u = 0.5 + 0.48 * (vx / max(max_arm_span, 1e-4))
            v_coord = (vy - y_bottom) / max(length, 1e-4)
            u = max(0.01, min(0.99, u))
            v_coord = max(0.01, min(0.99, v_coord))
            uvs.append([u, v_coord])

        # Xây dựng Trimesh object
        mesh_vertices = np.array(all_vertices, dtype=np.float64)
        mesh_faces = np.array(all_faces, dtype=np.int64)
        mesh_uvs = np.array(uvs, dtype=np.float64)

        mesh = trimesh.Trimesh(vertices=mesh_vertices, faces=mesh_faces, process=True)
        # Đảm bảo pháp tuyến hướng ra ngoài
        mesh.fix_normals()

        # Gán Texture nếu có ảnh
        if texture_image is not None:
            try:
                from PIL import Image as PILImage
                if isinstance(texture_image, PILImage.Image):
                    # Đảm bảo ảnh là RGB
                    img_rgb = texture_image.convert("RGB")
                    material = trimesh.visual.material.PBRMaterial(
                        baseColorTexture=img_rgb,
                        metallicFactor=0.0,
                        roughnessFactor=0.75,
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
        """Sinh mesh 3D trực tiếp từ một GarmentChart và mã Size."""
        spec = chart.get_size(size)
        return self.generate_tshirt(spec, texture_image=texture_image)

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
