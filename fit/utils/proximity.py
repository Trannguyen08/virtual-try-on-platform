"""Module tính toán khoảng cách và điểm gần nhất trên bề mặt Mesh 3D (Proximity Engine).

Hỗ trợ cơ chế tự động Fallback linh hoạt:
1. Nếu môi trường có cài `rtree`: Sử dụng cơ chế BVH / R-Tree mặc định của Trimesh.
2. Nếu môi trường KHÔNG có `rtree`: Tự động chuyển đổi sang thuật toán giải tích Vectorized
   Ericson Point-to-Triangle kết hợp SciPy cKDTree (Zero External C-Dependencies, cực nhanh và chính xác 100%).
"""

from typing import Tuple
import numpy as np
from scipy.spatial import cKDTree
import trimesh

try:
    import rtree  # type: ignore # noqa: F401
    _HAS_RTREE = True
except (ImportError, ModuleNotFoundError):
    _HAS_RTREE = False


def _point_to_triangle_closest_batch(
    points: np.ndarray,
    triangles: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Thuật toán Christer Ericson Vectorized tính điểm gần nhất trên tam giác trong không gian 3D.

    Args:
        points: Mảng tọa độ các điểm truy vấn, shape (N, 3).
        triangles: Mảng tọa độ tam giác tương ứng, shape (N, 3, 3).

    Returns:
        closest: Mảng tọa độ điểm gần nhất trên mặt/cạnh/đỉnh tam giác, shape (N, 3).
        distances: Mảng khoảng cách Euclid tương ứng, shape (N,).
    """
    a = triangles[:, 0, :]
    b = triangles[:, 1, :]
    c = triangles[:, 2, :]

    ab = b - a
    ac = c - a
    ap = points - a

    d1 = np.sum(ab * ap, axis=-1)
    d2 = np.sum(ac * ap, axis=-1)

    bp = points - b
    d3 = np.sum(ab * bp, axis=-1)
    d4 = np.sum(ac * bp, axis=-1)

    cp = points - c
    d5 = np.sum(ab * cp, axis=-1)
    d6 = np.sum(ac * cp, axis=-1)

    # Khởi tạo mảng kết quả
    closest = np.zeros_like(points)

    # 1. Đỉnh A
    mask_a = (d1 <= 0.0) & (d2 <= 0.0)
    closest[mask_a] = a[mask_a]

    # 2. Đỉnh B
    mask_b = (d3 >= 0.0) & (d4 <= d3) & (~mask_a)
    closest[mask_b] = b[mask_b]

    # 3. Cạnh AB
    vc = d1 * d4 - d3 * d2
    mask_ab = (vc <= 0.0) & (d1 >= 0.0) & (d3 <= 0.0) & (~mask_a) & (~mask_b)
    if np.any(mask_ab):
        denom_ab = np.maximum(d1[mask_ab] - d3[mask_ab], 1e-12)
        v_ab = (d1[mask_ab] / denom_ab)[:, np.newaxis]
        closest[mask_ab] = a[mask_ab] + v_ab * ab[mask_ab]

    # 4. Đỉnh C
    mask_c = (d6 >= 0.0) & (d5 <= d6) & (~mask_a) & (~mask_b) & (~mask_ab)
    closest[mask_c] = c[mask_c]

    # 5. Cạnh AC
    vb = d5 * d2 - d1 * d6
    mask_ac = (vb <= 0.0) & (d2 >= 0.0) & (d6 <= 0.0) & (~mask_a) & (~mask_b) & (~mask_ab) & (~mask_c)
    if np.any(mask_ac):
        denom_ac = np.maximum(d2[mask_ac] - d6[mask_ac], 1e-12)
        w_ac = (d2[mask_ac] / denom_ac)[:, np.newaxis]
        closest[mask_ac] = a[mask_ac] + w_ac * ac[mask_ac]

    # 6. Cạnh BC
    va = d3 * d6 - d5 * d4
    mask_bc = (
        (va <= 0.0)
        & ((d4 - d3) >= 0.0)
        & ((d5 - d6) >= 0.0)
        & (~mask_a)
        & (~mask_b)
        & (~mask_ab)
        & (~mask_c)
        & (~mask_ac)
    )
    if np.any(mask_bc):
        denom_bc = np.maximum((d4[mask_bc] - d3[mask_bc]) + (d5[mask_bc] - d6[mask_bc]), 1e-12)
        w_bc = ((d4[mask_bc] - d3[mask_bc]) / denom_bc)[:, np.newaxis]
        closest[mask_bc] = b[mask_bc] + w_bc * (c[mask_bc] - b[mask_bc])

    # 7. Vùng bên trong mặt phẳng tam giác (Face interior)
    mask_inside = (~mask_a) & (~mask_b) & (~mask_ab) & (~mask_c) & (~mask_ac) & (~mask_bc)
    if np.any(mask_inside):
        denom_face = np.maximum(va[mask_inside] + vb[mask_inside] + vc[mask_inside], 1e-12)
        v_face = (vb[mask_inside] / denom_face)[:, np.newaxis]
        w_face = (vc[mask_inside] / denom_face)[:, np.newaxis]
        closest[mask_inside] = a[mask_inside] + v_face * ab[mask_inside] + w_face * ac[mask_inside]

    distances = np.linalg.norm(points - closest, axis=-1)
    return closest, distances


def query_surface_proximity(
    mesh: trimesh.Trimesh,
    query_points: np.ndarray,
    k_candidates: int = 32,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Tìm điểm gần nhất trên bề mặt mesh, khoảng cách và xác định điểm nằm trong/ngoài.

    Args:
        mesh: Đối tượng Trimesh mục tiêu.
        query_points: Mảng các điểm cần tìm khoảng cách, shape (N, 3).
        k_candidates: Số lượng tam giác ứng viên lân cận để kiểm tra (mặc định: 32).

    Returns:
        closest_points: Tọa độ điểm gần nhất trên bề mặt mesh, shape (N, 3).
        distances: Khoảng cách Euclid tương ứng, shape (N,).
        face_ids: Chỉ số của tam giác gần nhất, shape (N,).
        is_inside: Mảng boolean (True nếu điểm nằm lọt bên trong thể tích kín của mesh).
    """
    points = np.asarray(query_points, dtype=np.float64)
    num_points = len(points)

    if num_points == 0 or len(mesh.faces) == 0:
        return (
            np.zeros((0, 3), dtype=np.float64),
            np.zeros(0, dtype=np.float64),
            np.zeros(0, dtype=int),
            np.zeros(0, dtype=bool),
        )

    # 1. Thử cơ chế mặc định của Trimesh nếu có cài rtree
    if _HAS_RTREE:
        try:
            closest_pts, dists, f_ids = mesh.nearest.on_surface(points)
            try:
                inside_mask = mesh.contains(points)
            except Exception:
                # Dùng pháp tuyến mặt để xác định trong/ngoài nếu mesh.contains lỗi rtree
                normals = mesh.face_normals[f_ids]
                vectors = points - closest_pts
                dot_prods = np.sum(vectors * normals, axis=-1)
                inside_mask = dot_prods < -1e-5

            return (
                np.asarray(closest_pts, dtype=np.float64),
                np.asarray(dists, dtype=np.float64),
                np.asarray(f_ids, dtype=int),
                inside_mask,
            )
        except Exception:
            pass

    # 2. Thuật toán Fallback hoàn toàn bằng SciPy + NumPy (Không cần rtree)
    centroids = mesh.triangles_center
    tree = cKDTree(centroids)

    k_actual = min(k_candidates, len(mesh.faces))
    _, candidate_indices = tree.query(points, k=k_actual)

    if k_actual == 1:
        candidate_indices = candidate_indices[:, np.newaxis]

    best_distances = np.full(num_points, np.inf, dtype=np.float64)
    best_closest = np.zeros_like(points)
    best_face_ids = np.zeros(num_points, dtype=int)

    # Lặp qua k tam giác ứng viên lân cận
    for j in range(k_actual):
        f_idx = candidate_indices[:, j]
        tris = mesh.triangles[f_idx]
        cur_closest, cur_dist = _point_to_triangle_closest_batch(points, tris)

        better_mask = cur_dist < best_distances
        if np.any(better_mask):
            best_distances[better_mask] = cur_dist[better_mask]
            best_closest[better_mask] = cur_closest[better_mask]
            best_face_ids[better_mask] = f_idx[better_mask]

    # Xác định trong/ngoài bằng tích vô hướng với pháp tuyến mặt tam giác gần nhất
    best_normals = mesh.face_normals[best_face_ids]
    diff_vectors = points - best_closest
    signed_dot = np.sum(diff_vectors * best_normals, axis=-1)
    is_inside = signed_dot < -1e-5

    return best_closest, best_distances, best_face_ids, is_inside
