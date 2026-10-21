"""
Unit Tests for Garment Simulation & Draping
Target: TC-GAR-05, TC-GAR-06
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest
import trimesh

from garment.simulation.draping import GeometricClothDraper, DrapingError
from garment.simulation.simulator import ClothSimulator
from garment.mesh.mesh_generator import GarmentMeshGenerator
from garment.size_chart.garment_loader import SizeMeasurement
from garment.reconstruction.validation import GlbValidator


def _create_mock_body_mesh() -> trimesh.Trimesh:
    """Tạo body proxy mẫu (hình trụ elip mô phỏng thân người) cho kiểm thử."""
    # Bán trục thân người: rộng vai 40cm, sâu ngực 24cm, cao từ 0.0m đến 1.70m
    body = trimesh.creation.cylinder(radius=0.14, height=1.60, sections=32)
    # Dịch chuyển sao cho chân ở Y=0, đỉnh đầu ở Y=1.60m
    body.apply_translation([0, 0.80, 0])
    return body


@pytest.mark.fast
def test_geometric_draping_tc_gar_05():
    """
    Test Case ID: TC-GAR-05
    Target: Mô phỏng vải hoàn tất trên body mẫu.
    Expected: Áo ôm ổn định quanh thân người, không rơi tự do, không có đỉnh bị lỗi NaN.
    """
    body = _create_mock_body_mesh()
    generator = GarmentMeshGenerator(base_y_offset=0.90)
    spec = SizeMeasurement(
        size="M",
        chest_cm=100.0,
        waist_cm=96.0,
        hem_cm=100.0,
        shoulder_width_cm=44.0,
        length_cm=69.0,
    )
    garment = generator.generate_tshirt(spec)

    draper = GeometricClothDraper(min_clearance_m=0.005, target_clearance_m=0.015)
    draped = draper.drape(body_mesh=body, garment_mesh=garment)

    # 1. Không chứa tọa độ NaN hoặc Inf
    assert not np.isnan(draped.vertices).any(), "Có đỉnh chứa tọa độ NaN"
    assert not np.isinf(draped.vertices).any(), "Có đỉnh chứa tọa độ Inf"

    # 2. Không rơi tự do: Trọng tâm Y của áo phải nằm ổn định trong vùng thân người (0.8m - 1.5m)
    mean_y = float(np.mean(draped.vertices[:, 1]))
    assert 0.85 <= mean_y <= 1.45, f"Áo bị rơi tự do xuống Y={mean_y:.2f}m"

    # 3. Khoảng cách an toàn chống xuyên thủng da:
    # Khoảng cách tối thiểu từ các đỉnh áo đến bề mặt cơ thể phải >= 0.004m (xấp xỉ 5mm)
    from trimesh import proximity
    _, distances, _ = proximity.closest_point(body, draped.vertices)
    min_dist = float(np.min(distances))
    assert min_dist >= 0.0035, f"Khoảng hở tối thiểu {min_dist*1000:.1f}mm bị lẹm vào da (< 3.5mm)"


@pytest.mark.fast
def test_cloth_simulator_export_glb_tc_gar_06():
    """
    Test Case ID: TC-GAR-06
    Target: Gọi ClothSimulator.simulate() xuất file draped.glb hợp lệ, không treo máy.
    Expected: File .glb được xuất thành công, đạt chuẩn glTF 2.0 theo GlbValidator.
    """
    body = _create_mock_body_mesh()
    generator = GarmentMeshGenerator(base_y_offset=0.90)
    spec = SizeMeasurement(
        size="M",
        chest_cm=100.0,
        waist_cm=96.0,
        hem_cm=100.0,
        shoulder_width_cm=44.0,
        length_cm=69.0,
    )
    garment = generator.generate_tshirt(spec)

    simulator = ClothSimulator()

    with tempfile.TemporaryDirectory() as tmpdir:
        out_glb = Path(tmpdir) / "draped.glb"

        # Chạy simulation (chế độ auto sẽ fallback an toàn sang Geometric nếu không có Blender)
        result_path = simulator.simulate(
            body_input=body,
            garment_input=garment,
            output_glb_path=out_glb,
            prefer_engine="geometric",
        )

        assert result_path.is_file() and result_path.stat().st_size > 0

        # Kiểm định bằng GlbValidator
        validator = GlbValidator()
        meta = validator.validate(result_path)
        assert meta.triangle_count is not None and meta.triangle_count > 0
        assert meta.file_size_bytes > 1000
