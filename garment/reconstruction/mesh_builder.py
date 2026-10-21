from __future__ import annotations

import math
from typing import Any

import cv2
import numpy as np
import trimesh
from PIL import Image

from .errors import ReconstructionError


class GarmentMeshBuilder:
    """3D parametric mesh generator for reconstructed garments.

    Features:
    - Organic curvature with soft rounded silhouette seams.
    - Completely hollow, see-through bottom hem opening (no pinching or stray bridging faces).
    - Open neck collar and sleeve cuffs.
    - Outward texture color inpainting (eliminates Three.js edge bleed).
    - Double-sided PBR materials for realistic inside/outside view.
    """

    def __init__(self, grid_resolution: int = 128) -> None:
        self.grid_resolution = grid_resolution

    def build_mesh(
        self,
        *,
        front_rgb: np.ndarray,
        back_rgb: np.ndarray | None,
        mask: np.ndarray,
        garment_type: str,
        meters_per_pixel: float,
        landmarks: dict[str, tuple[float, float]],
    ) -> dict[str, Any]:
        ys, xs = np.nonzero(mask)
        x0, x1 = float(xs.min()), float(xs.max())
        y0, y1 = float(ys.min()), float(ys.max())
        box_width = max(1.0, x1 - x0)
        box_height = max(1.0, y1 - y0)
        center_x = (x0 + x1) / 2.0
        center_y = (y0 + y1) / 2.0

        # Smooth the mask before grid generation to eliminate staircase saw-teeth
        _blur = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), sigmaX=3.0, sigmaY=3.0)
        _m8 = (_blur > 0.45).astype(np.uint8)
        _sm_k = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (max(5, int(box_width * 0.018)), max(5, int(box_height * 0.018))),
        )
        _m8 = cv2.morphologyEx(_m8, cv2.MORPH_CLOSE, _sm_k, iterations=2)
        mesh_mask: np.ndarray = _m8.astype(bool)

        nx = self.grid_resolution
        ny = max(24, int(round(nx * box_height / box_width)))
        ny = min(ny, self.grid_resolution * 2)
        grid_x = np.linspace(x0, x1, nx + 1)
        grid_y = np.linspace(y0, y1, ny + 1)

        def row_extent(pixel_y: float) -> tuple[float, float]:
            target = min(max(int(round(pixel_y)), 0), mesh_mask.shape[0] - 1)
            for offset in range(0, max(3, int(box_height * 0.04))):
                for candidate in (target + offset, target - offset):
                    if 0 <= candidate < mesh_mask.shape[0]:
                        values = np.flatnonzero(mesh_mask[candidate])
                        if len(values) >= 2:
                            return float(values.min()), float(values.max())
            return x0, x1

        def col_extent(pixel_x: float) -> tuple[float, float]:
            target = min(max(int(round(pixel_x)), 0), mesh_mask.shape[1] - 1)
            for offset in range(0, max(3, int(box_width * 0.04))):
                for candidate in (target + offset, target - offset):
                    if 0 <= candidate < mesh_mask.shape[1]:
                        values = np.flatnonzero(mesh_mask[:, candidate])
                        if len(values) >= 2:
                            return float(values.min()), float(values.max())
            return y0, y1

        is_top = garment_type in {"tshirt", "shirt", "jacket", "dress"}
        crotch_y = landmarks.get("crotch_center", (center_x, y0 + box_height * 0.45))[1]

        if garment_type in {"pants", "skirt"}:
            hip_l = landmarks.get("hip_left", (x0 + box_width * 0.25, y0 + box_height * 0.25))
            hip_r = landmarks.get("hip_right", (x1 - box_width * 0.25, y0 + box_height * 0.25))
            torso_w_px = max(1.0, abs(hip_r[0] - hip_l[0]))
            torso_w_m = torso_w_px * meters_per_pixel
            base_depth = max(0.055, min(0.12, torso_w_m * 0.24))
            body_depth = base_depth
            z_edge = 0.0012
            z_shoulder = base_depth
            z_cuff = base_depth
            left_armpit_x = x0
            right_armpit_x = x1
            armpit_y = y0 + box_height * 0.38
        else:
            armpit_l = landmarks.get("left_armpit", (center_x - box_width * 0.26, y0 + box_height * 0.38))
            armpit_r = landmarks.get("right_armpit", (center_x + box_width * 0.26, y0 + box_height * 0.38))
            waist_l = landmarks.get("waist_left", (center_x - box_width * 0.24, y0 + box_height * 0.70))
            waist_r = landmarks.get("waist_right", (center_x + box_width * 0.24, y0 + box_height * 0.70))
            chest_w_px = abs(armpit_r[0] - armpit_l[0])
            waist_w_px = abs(waist_r[0] - waist_l[0])
            torso_w_px = max(1.0, max(chest_w_px, waist_w_px))
            torso_w_m = torso_w_px * meters_per_pixel
            body_depth = max(0.026, min(0.034, torso_w_m * 0.068))
            base_depth = body_depth
            z_apex = 0.005
            z_edge = 0.0012
            left_armpit_x = armpit_l[0]
            right_armpit_x = armpit_r[0]
            armpit_y = min(armpit_l[1], armpit_r[1])
            z_shoulder = body_depth * 0.60
            z_cuff = body_depth * 0.40

        def get_depth_factor(v: float) -> float:
            if garment_type in {"pants", "skirt"}:
                if v < 0.15:
                    return 0.70 + 0.30 * (v / 0.15)
                elif v < 0.45:
                    return 1.0
                else:
                    return 1.0 - 0.40 * ((v - 0.45) / 0.55)
            else:
                if v < 0.14:
                    return 0.28 + 0.20 * (v / 0.14)
                elif v < 0.42:
                    t = (v - 0.14) / 0.28
                    return 0.48 + 0.52 * math.sin(t * (math.pi / 2.0))
                elif v < 0.72:
                    t = (v - 0.42) / 0.30
                    return 1.0 - 0.12 * t
                else:
                    t = (v - 0.72) / 0.28
                    return 0.88 - 0.08 * t

        collar_half_w_px = max(1.0, min(box_width * 0.12, torso_w_px * 0.20))
        collar_drop_y_px = max(4.0, box_height * 0.038)
        neck_opening = (center_x, y0, collar_half_w_px, collar_drop_y_px, box_height)

        def is_in_neck_opening(test_px: float, test_py: float) -> bool:
            if not is_top:
                return False
            dx = abs(test_px - center_x)
            if dx >= collar_half_w_px:
                return False
            u = dx / collar_half_w_px
            y_cut = y0 + collar_drop_y_px * math.sqrt(max(0.0, 1.0 - u * u))
            return test_py < y_cut

        def get_z_at(test_px: float, test_py: float) -> float:
            if not is_top:
                rel_y = max(0.0, min(1.0, (test_py - y0) / box_height))
                depth_factor = get_depth_factor(rel_y)
                peak_z = base_depth * depth_factor
                edge_z = max(0.005, min(0.012, peak_z * 0.12))
                if garment_type == "pants" and test_py > crotch_y:
                    row_l, row_r = row_extent(test_py)
                    if test_px < center_x:
                        leg_center = (row_l + center_x) / 2.0
                        leg_half_w = max((center_x - row_l) / 2.0, 1.0)
                    else:
                        leg_center = (center_x + row_r) / 2.0
                        leg_half_w = max((row_r - center_x) / 2.0, 1.0)
                    norm_x = max(-1.0, min(1.0, (test_px - leg_center) / leg_half_w))
                    curvature = math.sqrt(max(0.0, 1.0 - norm_x**2))
                    return edge_z + (peak_z - edge_z) * curvature
                col_top, col_bot = col_extent(test_px)
                col_h = max(col_bot - col_top, 1.0)
                col_cy = (col_top + col_bot) / 2.0
                norm_y = max(-1.0, min(1.0, (test_py - col_cy) / (col_h / 2.0)))
                curvature = math.sqrt(max(0.0, 1.0 - norm_y**2))
                return edge_z + (peak_z - edge_z) * curvature

            # ── TOPS ──────────────────────────────────────────────────────────
            if test_py >= armpit_y:
                row_l, row_r = row_extent(test_py)
                row_w = max(1.0, row_r - row_l)
                row_cx = (row_l + row_r) / 2.0
                u = min(1.0, max(0.0, abs(test_px - row_cx) / (row_w / 2.0)))
                curve_x = math.sqrt(max(0.0, 1.0 - u * u))
                horiz_z = z_edge + (body_depth - z_edge) * curve_x
                rel_y = max(0.0, min(1.0, (test_py - armpit_y) / max(1.0, y1 - armpit_y)))
                drape = 1.0 - 0.03 * math.sin(rel_y * math.pi) + 0.015 * math.sin(u * math.pi * 3.0) * rel_y
                return max(z_edge, horiz_z * drape)

            # Above armpit_y
            frac_y = max(0.0, min(1.0, (test_py - y0) / max(1.0, armpit_y - y0)))
            shoulder_half = torso_w_px * 0.37
            armhole_l = (center_x - shoulder_half) * (1.0 - frac_y) + left_armpit_x * frac_y
            armhole_r = (center_x + shoulder_half) * (1.0 - frac_y) + right_armpit_x * frac_y

            if armhole_l <= test_px <= armhole_r:
                torso_half = max(1.0, (armhole_r - armhole_l) / 2.0)
                torso_cx = (armhole_l + armhole_r) / 2.0
                u = min(1.0, max(0.0, abs(test_px - torso_cx) / torso_half))
                curve_x = math.sqrt(max(0.0, 1.0 - u * u))
                torso_peak_z = z_shoulder + (body_depth - z_shoulder) * curve_x
                vert_factor = 0.35 + 0.65 * math.sin(frac_y * (math.pi / 2.0))
                return max(z_apex, torso_peak_z * vert_factor)
            else:
                if test_px < armhole_l:
                    span = max(1.0, armhole_l - x0)
                    u_sleeve = min(1.0, max(0.0, (armhole_l - test_px) / span))
                else:
                    span = max(1.0, x1 - armhole_r)
                    u_sleeve = min(1.0, max(0.0, (test_px - armhole_r) / span))

                col_top, col_bot = col_extent(test_px)
                col_h = max(col_bot - col_top, 1.0)
                col_cy = (col_top + col_bot) / 2.0
                norm_y = max(-1.0, min(1.0, (test_py - col_cy) / (col_h / 2.0)))
                tube_curve = math.sqrt(max(0.0, 1.0 - norm_y * norm_y))
                sleeve_base_z = z_shoulder - u_sleeve * (z_shoulder - z_cuff)

                if u_sleeve <= 0.30:
                    cuff_round = 1.0
                else:
                    w = (u_sleeve - 0.30) / 0.70
                    cuff_round = math.sqrt(max(0.0, 1.0 - w * w))

                peak_sleeve_z = z_edge + (sleeve_base_z - z_edge) * cuff_round
                return max(z_edge, z_edge + (peak_sleeve_z - z_edge) * tube_curve)

        cell_faces: list[tuple[int, int, tuple[tuple[int, int], ...]]] = []
        for row in range(ny):
            for column in range(nx):
                corners = (
                    (row, column),
                    (row + 1, column),
                    (row, column + 1),
                    (row + 1, column + 1),
                )
                for face in (
                    (corners[0], corners[1], corners[2]),
                    (corners[2], corners[1], corners[3]),
                ):
                    px = int(round(np.mean([grid_x[node[1]] for node in face])))
                    py = int(round(np.mean([grid_y[node[0]] for node in face])))
                    px = min(max(px, 0), mesh_mask.shape[1] - 1)
                    py = min(max(py, 0), mesh_mask.shape[0] - 1)
                    if mesh_mask[py, px] and not is_in_neck_opening(px, py):
                        cell_faces.append((row, column, face))

        if len(cell_faces) < 24:
            raise ReconstructionError(
                "GARMENT_MESH_TOO_SPARSE",
                "The segmented garment is too small to reconstruct",
                http_status=422,
            )

        nodes = sorted(
            {
                node
                for _row, _column, face in cell_faces
                for node in face
            }
        )
        node_index = {node: index for index, node in enumerate(nodes)}

        front_faces: list[tuple[int, int, int]] = []
        back_faces: list[tuple[int, int, int]] = []
        for _row, _column, (first, second, third) in cell_faces:
            front_faces.append(
                (node_index[first], node_index[second], node_index[third])
            )
            back_faces.append(
                (node_index[first], node_index[third], node_index[second])
            )

        boundary_edges = self._boundary_edges(front_faces)

        # Smooth boundary vertices
        raw_pixels = [(float(grid_x[column]), float(grid_y[row])) for row, column in nodes]
        boundary_adj: dict[int, list[int]] = {}
        for u, v in boundary_edges:
            boundary_adj.setdefault(u, []).append(v)
            boundary_adj.setdefault(v, []).append(u)

        node_pixels = list(raw_pixels)
        for _ in range(4):
            prev = list(node_pixels)
            for idx, neighbors in boundary_adj.items():
                if len(neighbors) == 2:
                    n1, n2 = neighbors
                    node_pixels[idx] = (
                        0.5 * prev[idx][0] + 0.25 * (prev[n1][0] + prev[n2][0]),
                        0.5 * prev[idx][1] + 0.25 * (prev[n1][1] + prev[n2][1]),
                    )

        front_vertices = []
        back_vertices = []
        uvs = []
        for index, (row, column) in enumerate(nodes):
            px, py = node_pixels[index]
            z = get_z_at(px, py)
            x = (px - center_x) * meters_per_pixel
            y = (center_y - py) * meters_per_pixel
            front_vertices.append((x, y, z))
            back_vertices.append((x, y, -z))
            uvs.append((px / max(1, mask.shape[1] - 1), 1.0 - py / max(1, mask.shape[0] - 1)))

        seam_vertices: list[tuple[float, float, float]] = []
        seam_uvs: list[tuple[float, float]] = []
        seam_faces: list[tuple[int, int, int]] = []
        opening_vertices: dict[str, set[int]] = {}

        # ── Feature 4: Hollow See-Through Bottom Hem Opening ─────────────────────
        # All edges along the bottom hem of the torso are left COMPLETELY OPEN.
        # Zero seam bridging faces are created at the bottom, so looking from below
        # you see straight through the hollow cavity of the shirt.
        for first, second in boundary_edges:
            p1 = node_pixels[first]
            p2 = node_pixels[second]
            midpoint = (
                (p1[0] + p2[0]) / 2.0,
                (p1[1] + p2[1]) / 2.0,
            )
            edge_vec = (p2[0] - p1[0], p2[1] - p1[1])

            opening = self._opening_name(
                midpoint,
                garment_type,
                x0=x0,
                x1=x1,
                y0=y0,
                y1=y1,
                landmarks=landmarks,
                neck_opening=neck_opening,
                edge_vec=edge_vec,
            )
            if opening:
                opening_vertices.setdefault(opening, set()).update((first, second))
                # Openings (neck, hem, cuffs, waist) are NEVER bridged!
                if opening in {"neck", "hem", "waist", "left_hem", "right_hem", "left_cuff", "right_cuff"}:
                    continue

            # Bridge closed silhouette side edges
            base = len(seam_vertices)
            seam_vertices.extend(
                (
                    front_vertices[first],
                    front_vertices[second],
                    back_vertices[second],
                    back_vertices[first],
                )
            )
            seam_uvs.extend(
                (
                    (0.0, 0.0),
                    (1.0, 0.0),
                    (1.0, 1.0),
                    (0.0, 1.0),
                )
            )
            seam_faces.extend(((base, base + 1, base + 2), (base, base + 2, base + 3)))

        front_mesh = trimesh.Trimesh(
            vertices=np.asarray(front_vertices),
            faces=np.asarray(front_faces),
            process=False,
        )
        _ = front_mesh.vertex_normals

        # Outward Color Inpainting (prevents Three.js mipmap edge bleed)
        fabric_color = np.median(front_rgb[mask], axis=0).astype(np.uint8)
        clean_front_rgb = front_rgb.copy()

        k_pad = np.ones((5, 5), dtype=np.uint8)
        dilated_mask = cv2.dilate(mask.astype(np.uint8), k_pad, iterations=2)
        outer_pad_band = (dilated_mask > 0) & (~mask)

        clean_front_rgb[~dilated_mask.astype(bool)] = fabric_color
        if np.any(outer_pad_band):
            inpaint_mask = outer_pad_band.astype(np.uint8) * 255
            clean_front_rgb = cv2.inpaint(
                clean_front_rgb, inpaint_mask, inpaintRadius=4, flags=cv2.INPAINT_TELEA
            )
        clean_front_rgb[~dilated_mask.astype(bool)] = fabric_color

        front_texture = Image.fromarray(clean_front_rgb)
        front_material = trimesh.visual.material.PBRMaterial(
            baseColorFactor=[1.0, 1.0, 1.0, 1.0],
            baseColorTexture=front_texture,
            metallicFactor=0.0,
            roughnessFactor=0.88,
            doubleSided=True,
        )
        front_mesh.visual = trimesh.visual.texture.TextureVisuals(
            uv=np.asarray(uvs, dtype=np.float32),
            material=front_material,
        )

        back_mesh = trimesh.Trimesh(
            vertices=np.asarray(back_vertices),
            faces=np.asarray(back_faces),
            process=False,
        )
        _ = back_mesh.vertex_normals

        if back_rgb is not None:
            back_image = back_rgb
        else:
            # Plain blank surface carrying the dominant base color of the front garment
            back_image = np.zeros_like(clean_front_rgb)
            back_image[:] = fabric_color

        back_texture = Image.fromarray(back_image)
        back_material = trimesh.visual.material.PBRMaterial(
            baseColorFactor=[1.0, 1.0, 1.0, 1.0],
            baseColorTexture=back_texture,
            metallicFactor=0.0,
            roughnessFactor=0.88,
            doubleSided=True,
        )
        back_mesh.visual = trimesh.visual.texture.TextureVisuals(
            uv=np.asarray(uvs, dtype=np.float32),
            material=back_material,
        )

        scene = trimesh.Scene()
        scene.add_geometry(front_mesh, node_name="GarmentFront", geom_name="GarmentFront")
        scene.add_geometry(back_mesh, node_name="GarmentBack", geom_name="GarmentBack")

        if seam_faces:
            seam_mesh = trimesh.Trimesh(
                vertices=np.asarray(seam_vertices),
                faces=np.asarray(seam_faces),
                process=False,
            )
            _ = seam_mesh.vertex_normals
            seam_color_img = np.zeros((16, 16, 3), dtype=np.uint8)
            seam_color_img[:] = fabric_color
            seam_texture = Image.fromarray(seam_color_img)
            seam_material = trimesh.visual.material.PBRMaterial(
                baseColorFactor=[1.0, 1.0, 1.0, 1.0],
                baseColorTexture=seam_texture,
                metallicFactor=0.0,
                roughnessFactor=0.92,
                doubleSided=True,
            )
            seam_mesh.visual = trimesh.visual.texture.TextureVisuals(
                uv=np.asarray(seam_uvs, dtype=np.float32),
                material=seam_material,
            )
            scene.add_geometry(
                seam_mesh, node_name="GarmentSeams", geom_name="GarmentSeams"
            )

        landmark_vertices: dict[str, dict[str, Any]] = {}
        pixel_array = np.asarray(node_pixels)
        for name, point in landmarks.items():
            nearest = int(np.argmin(np.sum((pixel_array - np.asarray(point)) ** 2, axis=1)))
            landmark_vertices[name] = {
                "front_vertex": nearest,
                "back_vertex": nearest,
                "front_position_m": [round(float(value), 6) for value in front_vertices[nearest]],
                "back_position_m": [round(float(value), 6) for value in back_vertices[nearest]],
            }

        openings = {
            name: {
                "mesh_nodes": ["GarmentFront", "GarmentBack"],
                "vertex_indices": sorted(indices),
            }
            for name, indices in opening_vertices.items()
        }
        return {
            "scene": scene,
            "front_vertex_count": len(front_vertices),
            "back_vertex_count": len(back_vertices),
            "triangle_count": len(front_faces) + len(back_faces) + len(seam_faces),
            "landmark_vertices": landmark_vertices,
            "openings": openings,
        }

    @staticmethod
    def _boundary_edges(faces: list[tuple[int, int, int]]) -> list[tuple[int, int]]:
        counts: dict[tuple[int, int], int] = {}
        orientation: dict[tuple[int, int], tuple[int, int]] = {}
        for face in faces:
            for first, second in (
                (face[0], face[1]),
                (face[1], face[2]),
                (face[2], face[0]),
            ):
                key = tuple(sorted((first, second)))
                counts[key] = counts.get(key, 0) + 1
                orientation[key] = (first, second)
        return [orientation[key] for key, count in counts.items() if count == 1]

    @staticmethod
    def _opening_name(
        point: tuple[float, float],
        garment_type: str,
        *,
        x0: float,
        x1: float,
        y0: float,
        y1: float,
        landmarks: dict[str, tuple[float, float]],
        neck_opening: tuple[float, float, float, float, float],
        edge_vec: tuple[float, float] = (0.0, 0.0),
        normal: tuple[float, float] = (0.0, 0.0),
    ) -> str | None:
        normalized_x = (point[0] - x0) / max(1.0, x1 - x0)
        normalized_y = (point[1] - y0) / max(1.0, y1 - y0)
        width = max(1.0, x1 - x0)
        height = max(1.0, y1 - y0)
        # Waist and hem openings run across the garment. A side edge near the
        # top/bottom must still connect the front and back panels.
        crosses_width = abs(edge_vec[0]) > abs(edge_vec[1])

        if garment_type == "pants":
            if normalized_y < 0.08 and crosses_width:
                return "waist"
            if normalized_y > 0.88 and crosses_width:
                return "left_hem" if normalized_x < 0.5 else "right_hem"
            return None

        if garment_type == "skirt":
            if normalized_y < 0.08 and crosses_width:
                return "waist"
            if normalized_y > 0.88 and crosses_width:
                return "hem"
            return None

        # ── Tops: Neck, Cuffs, and Hollow Bottom Hem ─────────────────────────────
        # 1. Neck Opening
        center_x, top_y, collar_half_w, collar_drop_y, _box_h = neck_opening
        dx = abs(point[0] - center_x)
        if dx < collar_half_w * 1.08:
            u = min(1.0, dx / collar_half_w)
            y_cut = top_y + collar_drop_y * math.sqrt(max(0.0, 1.0 - u * u))
            if point[1] <= y_cut + max(6.0, width * 0.025):
                return "neck"

        # 2. Sleeve Cuff Openings (left/right distal ends)
        left_armpit = landmarks.get("left_armpit")
        right_armpit = landmarks.get("right_armpit")
        if left_armpit is not None:
            sleeve_len_x = left_armpit[0] - x0
            if point[0] <= x0 + sleeve_len_x * 0.12:
                if abs(edge_vec[1]) >= abs(edge_vec[0]) * 0.65:
                    return "left_cuff"

        if right_armpit is not None:
            sleeve_len_x = x1 - right_armpit[0]
            if point[0] >= x1 - sleeve_len_x * 0.12:
                if abs(edge_vec[1]) >= abs(edge_vec[0]) * 0.65:
                    return "right_cuff"

        # 3. Bottom Hem Opening (Hollow See-Through Opening)
        # Any boundary edge along the bottom margin of the torso is the hem opening.
        # This completely guarantees that NO bridging seam faces close the bottom.
        waist_left = landmarks.get("waist_left", (x0 + width * 0.20, y1))
        waist_right = landmarks.get("waist_right", (x1 - width * 0.20, y1))
        torso_left = min(waist_left[0], landmarks.get("hem_left", waist_left)[0])
        torso_right = max(waist_right[0], landmarks.get("hem_right", waist_right)[0])

        if crosses_width and point[1] >= y1 - max(12.0, height * 0.065):
            # Across the entire torso width at the bottom, mark as hem opening!
            if (torso_left - max(8.0, width * 0.03)) <= point[0] <= (torso_right + max(8.0, width * 0.03)):
                return "hem"

        return None
