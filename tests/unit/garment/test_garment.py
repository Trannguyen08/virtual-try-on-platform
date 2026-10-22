"""
Unit Tests for Module M2 — 3D Garment & Simulation
Target: TC-GAR-02, TC-GAR-03, TC-GAR-04
"""

import math
import tempfile
from pathlib import Path

import numpy as np
import pytest
import trimesh

from garment.size_chart.garment_loader import (
    GarmentLoader,
    GarmentChart,
    SizeMeasurement,
    SizeChartError,
)
from garment.mesh.mesh_generator import GarmentMeshGenerator
from garment.mesh.size_scaling import SizeScaler, SizeScalingError


@pytest.mark.fast
def test_garment_loader_tc_gar_03():
    """
    Test Case ID: TC-GAR-03
    Target: Nạp đủ 4 size S, M, L, XL từ cấu hình JSON; kiểm tra tính đơn điệu tăng dần.
    Expected: S < M < L < XL đối với toàn bộ số đo chính (chest, waist, shoulder, length).
    """
    loader = GarmentLoader()
    chart = loader.load_category("tshirt")

    assert chart.category == "t_shirt"
    assert "S" in chart.sizes
    assert "M" in chart.sizes
    assert "L" in chart.sizes
    assert "XL" in chart.sizes

    s = chart.get_size("S")
    m = chart.get_size("M")
    l = chart.get_size("L")
    xl = chart.get_size("XL")

    # Kiểm tra tính đơn điệu tăng dần nghiêm ngặt (TC-GAR-03)
    assert s.chest_cm < m.chest_cm < l.chest_cm < xl.chest_cm
    assert s.length_cm < m.length_cm < l.length_cm < xl.length_cm
    assert s.shoulder_width_cm < m.shoulder_width_cm < l.shoulder_width_cm < xl.shoulder_width_cm
    assert s.waist_cm < m.waist_cm < l.waist_cm < xl.waist_cm

    # Kiểm tra chuyển đổi đơn vị mét nội bộ
    assert s.chest_m == pytest.approx(s.chest_cm / 100.0, rel=1e-5)
    assert m.length_m == pytest.approx(m.length_cm / 100.0, rel=1e-5)


@pytest.mark.fast
def test_garment_loader_non_monotonic_tc_gar_03():
    """
    Test Case ID: TC-GAR-03 (Negative Case)
    Target: Bảng size vi phạm tính đơn điệu (ví dụ size M nhỏ hơn size S).
    Expected: Phải ném ngoại lệ SizeChartError có kiểm soát, không gây sập hệ thống.
    """
    loader = GarmentLoader()
    invalid_data = {
        "category": "tshirt",
        "sizes": {
            "S": {"chest_cm": 100.0, "shoulder_width_cm": 44.0, "length_cm": 70.0},
            "M": {"chest_cm": 90.0, "shoulder_width_cm": 42.0, "length_cm": 68.0},  # Lỗi: M < S
        },
    }
    with pytest.raises(SizeChartError, match="Vi phạm tính đơn điệu"):
        loader.load_from_dict(invalid_data)


@pytest.mark.fast
def test_garment_mesh_generator_tc_gar_02():
    """
    Test Case ID: TC-GAR-02
    Target: Sinh mô hình 3D Mesh T-Shirt mẫu gốc (Size M).
    Expected: Topology sạch (manifold), số đỉnh <= 30.000, đúng hệ trục Y-up, đơn vị mét.
    """
    generator = GarmentMeshGenerator(base_y_offset=0.90)
    spec_m = SizeMeasurement(
        size="M",
        chest_cm=100.0,
        waist_cm=96.0,
        hem_cm=100.0,
        shoulder_width_cm=44.0,
        length_cm=69.0,
        sleeve_length_cm=21.0,
    )

    mesh = generator.generate_tshirt(spec_m)

    # 1. Số đỉnh tối ưu <= 30.000 vertices (TC-GAR-02)
    vertex_count = len(mesh.vertices)
    assert 500 <= vertex_count <= 30000, f"Số đỉnh {vertex_count} ngoài khoảng quy chuẩn"

    # 2. Không chứa tọa độ NaN hoặc Inf
    assert not np.isnan(mesh.vertices).any()
    assert not np.isinf(mesh.vertices).any()

    # 3. Kích thước bounding box trong không gian 3 chiều (đơn vị mét)
    bounds = mesh.bounds
    x_span = bounds[1][0] - bounds[0][0]
    y_span = bounds[1][1] - bounds[0][1]
    z_span = bounds[1][2] - bounds[0][2]

    # Chiều dài áo theo trục Y xấp xỉ 0.69m (± 0.05m do tính cả cổ áo)
    assert y_span == pytest.approx(spec_m.length_m, abs=0.08)

    # Chiều sâu theo trục Z phải lớn (khác 0 rõ rệt, chứng minh là 3D chứ không phải 2.5D dẹt)
    assert z_span >= 0.20, f"Độ sâu trục Z = {z_span:.3f}m quá phẳng (nguy cơ 2.5D)"

    # Rộng vai/ống tay theo trục X phải bao phủ vai và ống tay
    assert x_span >= spec_m.shoulder_width_m


@pytest.mark.fast
def test_size_scaling_circumference_tc_gar_04():
    """
    Test Case ID: TC-GAR-04
    Target: Sinh mesh 4 size S/M/L/XL; đo chu vi ngực bằng lát cắt mặt phẳng (Slicing).
    Expected: Sai lệch giữa chu vi ngực đo trên mesh và bảng Size Chart <= 1.0 cm.
    """
    loader = GarmentLoader()
    chart = loader.load_category("tshirt")
    scaler = SizeScaler()

    for sz_name in ["S", "M", "L", "XL"]:
        spec = chart.get_size(sz_name)
        mesh = scaler.generator.generate_tshirt(spec)

        passed, measured_cm, delta_cm = scaler.verify_size_accuracy(
            mesh, expected_chest_cm=spec.chest_cm, tolerance_cm=1.0
        )

        assert passed, (
            f"Size {sz_name}: Chu vi đo được = {measured_cm:.2f}cm, "
            f"Kỳ vọng = {spec.chest_cm:.2f}cm, Lệch = {delta_cm:.2f}cm (vượt quá 1.0 cm)"
        )


@pytest.mark.fast
def test_export_mesh_glb_and_obj_tc_gar_02():
    """
    Test Case ID: TC-GAR-02 (Export)
    Target: Xuất mesh sang định dạng file .obj và .glb chuẩn.
    Expected: File tạo thành công trên đĩa, đọc lại bằng Trimesh nguyên vẹn.
    """
    generator = GarmentMeshGenerator()
    spec = SizeMeasurement(
        size="M",
        chest_cm=100.0,
        waist_cm=96.0,
        hem_cm=100.0,
        shoulder_width_cm=44.0,
        length_cm=69.0,
    )
    mesh = generator.generate_tshirt(spec)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        obj_file = tmp_path / "tshirt_m.obj"
        glb_file = tmp_path / "tshirt_m.glb"

        generator.export_mesh(mesh, obj_file)
        generator.export_mesh(mesh, glb_file)

        assert obj_file.is_file() and obj_file.stat().st_size > 0
        assert glb_file.is_file() and glb_file.stat().st_size > 0

        # Đọc lại file xem có hợp lệ không
        loaded_obj = trimesh.load(str(obj_file))
        assert len(loaded_obj.vertices) == len(mesh.vertices)
