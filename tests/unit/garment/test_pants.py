"""
Unit Tests for Pants 3D & Pants Size Chart
Target: TC-GAR-02, TC-GAR-03, TC-GAR-04 (Pants Category)
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest
import trimesh

from garment.size_chart.garment_loader import (
    GarmentLoader,
    SizeMeasurement,
    SizeChartError,
)
from garment.mesh.pants_generator import PantsMeshGenerator
from garment.mesh.size_scaling import SizeScaler
from garment.reconstruction.validation import GlbValidator


@pytest.mark.fast
def test_pants_size_chart_monotonicity_tc_gar_03():
    """
    Test Case ID: TC-GAR-03 (Pants)
    Target: Bảng size quần pants.json tải đủ 4 size S, M, L, XL và tăng đơn điệu.
    Expected: S < M < L < XL đối với waist, hip, length.
    """
    loader = GarmentLoader()
    chart = loader.load_category("pants")

    assert chart.category == "pants"
    assert "S" in chart.sizes
    assert "M" in chart.sizes
    assert "L" in chart.sizes
    assert "XL" in chart.sizes

    s = chart.get_size("S")
    m = chart.get_size("M")
    l = chart.get_size("L")
    xl = chart.get_size("XL")

    # Kiểm tra tính tăng đơn điệu nghiêm ngặt
    assert s.waist_cm < m.waist_cm < l.waist_cm < xl.waist_cm
    assert s.hip_cm < m.hip_cm < l.hip_cm < xl.hip_cm
    assert s.length_cm < m.length_cm < l.length_cm < xl.length_cm


@pytest.mark.fast
def test_pants_mesh_generator_tc_gar_02():
    """
    Test Case ID: TC-GAR-02 (Pants)
    Target: Sinh mô hình Quần 3D Manifold thực thụ.
    Expected: Không phẳng (Z depth >= 0.18m), số đỉnh <= 30.000, 2 ống chân tách biệt.
    """
    generator = PantsMeshGenerator(ankle_y_offset=0.08)
    spec = SizeMeasurement(
        size="M",
        waist_cm=80.0,
        hip_cm=98.0,
        length_cm=100.0,
        inseam_cm=73.0,
        thigh_cm=58.0,
        hem_cm=36.0,
    )

    mesh = generator.generate_pants(spec)

    # 1. Số đỉnh tối ưu
    vertex_count = len(mesh.vertices)
    assert 500 <= vertex_count <= 30000

    # 2. Không chứa NaN/Inf
    assert not np.isnan(mesh.vertices).any()
    assert not np.isinf(mesh.vertices).any()

    # 3. Kích thước 3D
    bounds = mesh.bounds
    x_span = bounds[1][0] - bounds[0][0]
    y_span = bounds[1][1] - bounds[0][1]
    z_span = bounds[1][2] - bounds[0][2]

    # Chiều dài quần xấp xỉ 1.00m (± 0.05m)
    assert y_span == pytest.approx(spec.length_m, abs=0.05)

    # Chiều sâu thân hông (Z depth) phải >= 0.18m (đảm bảo 3D thực thụ, không dẹt 2.5D)
    assert z_span >= 0.18, f"Chiều sâu Z={z_span:.3f}m quá phẳng"

    # Chiều ngang bao trùm 2 chân
    assert x_span >= 0.30


@pytest.mark.fast
def test_pants_export_glb_tc_gar_02():
    """
    Test Case ID: TC-GAR-02 (Pants Export)
    Target: Xuất mô hình Quần 3D ra file GLB.
    Expected: File tạo thành công, hợp lệ theo GlbValidator.
    """
    generator = PantsMeshGenerator()
    spec = SizeMeasurement(
        size="M",
        waist_cm=80.0,
        hip_cm=98.0,
        length_cm=100.0,
        inseam_cm=73.0,
        thigh_cm=58.0,
        hem_cm=36.0,
    )
    mesh = generator.generate_pants(spec)

    with tempfile.TemporaryDirectory() as tmpdir:
        out_glb = Path(tmpdir) / "pants_m.glb"
        generator.export_mesh(mesh, out_glb)

        assert out_glb.is_file() and out_glb.stat().st_size > 0

        validator = GlbValidator()
        meta = validator.validate(out_glb)
        assert meta.triangle_count is not None and meta.triangle_count > 0


@pytest.mark.fast
def test_pants_waist_circumference_slicing_tc_gar_04():
    """
    Test Case ID: TC-GAR-04 (Pants Slicing)
    Target: Cắt lát cạp quần đo chu vi eo.
    Expected: Độ sai lệch so với bảng Size Chart <= 1.0 cm.
    """
    generator = PantsMeshGenerator(ankle_y_offset=0.08)
    spec = SizeMeasurement(
        size="M",
        waist_cm=80.0,
        hip_cm=98.0,
        length_cm=100.0,
        inseam_cm=73.0,
    )
    mesh = generator.generate_pants(spec)

    # Đo chu vi cạp quần (tại 98% chiều cao quần)
    bounds = mesh.bounds
    waist_y = float(bounds[0][1] + (bounds[1][1] - bounds[0][1]) * 0.98)
    measured_waist_cm = SizeScaler.measure_slice_circumference_cm(mesh, height_y=waist_y)

    delta_cm = abs(measured_waist_cm - spec.waist_cm)
    assert delta_cm <= 1.0, (
        f"Chu vi cạp quần đo được = {measured_waist_cm:.2f}cm, "
        f"Kỳ vọng = {spec.waist_cm:.2f}cm, Lệch = {delta_cm:.2f}cm (> 1.0cm)"
    )
