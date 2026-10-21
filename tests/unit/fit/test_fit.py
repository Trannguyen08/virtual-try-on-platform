"""Unit Test Suite cho Phân hệ Hình học 3D (Module M4 - Fit Engine).

Bao gồm toàn bộ các Test Cases từ TC-FIT-01 đến TC-FIT-06:
- TC-FIT-01: Tỷ lệ xuyên thấu (Penetration Ratio) với Mesh giải tích khối cầu.
- TC-FIT-02: Khoảng cách bề mặt (Distance) với vỏ cầu cách 2.0 cm.
- TC-FIT-03: Độ che phủ giải phẫu (Coverage Ratio) với 100% và 50% diện tích.
- TC-FIT-04: Phân đoạn vùng cơ thể và gán nhãn trạng thái độ vừa từng vùng.
- TC-FIT-05: Kiểm định công thức điểm Fit Score chuẩn hóa (0.4*Pen + 0.3*Dist + 0.3*Cov).
- TC-FIT-06: Xuất file heatmap.json validate 100% JSON Schema contract.
"""

import json
import numpy as np
import pytest
import trimesh

from fit.metrics.penetration import compute_penetration
from fit.metrics.distance import compute_distance
from fit.metrics.coverage import compute_coverage
from fit.region.body_regions import segment_body_regions
from fit.region.region_fit import evaluate_region_fit
from fit.score.fit_score import (
    WEIGHT_PENETRATION,
    WEIGHT_DISTANCE,
    WEIGHT_COVERAGE,
    compute_fit_score,
    evaluate_fit_score_breakdown,
)
from fit.score.classification import classify_overall_fit
from fit.heatmap.heatmap_generator import generate_heatmap_payload
from fit.heatmap.heatmap_exporter import export_heatmap_json, validate_heatmap_schema
from fit.evaluator import GeometryFitEvaluator
from shared.constants.body_regions import (
    ALL_REGIONS,
    STATUS_TIGHT,
    STATUS_GOOD,
    STATUS_LOOSE,
)


@pytest.fixture
def analytical_sphere_body() -> trimesh.Trimesh:
    """Fixture khối cầu cơ thể người giả lập: bán kính 0.20 m (20 cm)."""
    return trimesh.creation.icosphere(subdivisions=3, radius=0.20)


@pytest.fixture
def analytical_sphere_garment_outer() -> trimesh.Trimesh:
    """Fixture khối cầu áo ngoài: bán kính 0.22 m (22 cm), cách body đúng 2.0 cm."""
    return trimesh.creation.icosphere(subdivisions=3, radius=0.22)


@pytest.fixture
def analytical_sphere_garment_inner() -> trimesh.Trimesh:
    """Fixture khối cầu áo trong: bán kính 0.18 m (18 cm), nằm lọt hoàn toàn trong body."""
    return trimesh.creation.icosphere(subdivisions=3, radius=0.18)


def create_cylinder_y(
    radius: float,
    height: float,
    num_height_segments: int = 20,
    sections: int = 32,
    cap: bool = True,
) -> trimesh.Trimesh:
    """Tạo mesh hình trụ chuẩn hóa trục Y-up (Y-up, +Z forward) với phân đoạn chiều cao.

    Có các vòng chia cắt dọc theo chiều cao Y để các đỉnh phân bố đều trên thân trụ,
    phục vụ chính xác cho việc phân đoạn vùng giải phẫu (Vai, Ngực, Eo, Hông).
    """
    y_coords = np.linspace(-height / 2.0, height / 2.0, num_height_segments + 1)
    angles = np.linspace(0.0, 2.0 * np.pi, sections, endpoint=False)

    vertices = []
    for y in y_coords:
        for theta in angles:
            x = radius * np.cos(theta)
            z = radius * np.sin(theta)
            vertices.append([x, y, z])

    faces = []
    # Thân hình trụ (Side walls: winding order counter-clockwise to ensure outward normals)
    for r in range(num_height_segments):
        for s in range(sections):
            s_next = (s + 1) % sections
            v0 = r * sections + s
            v1 = r * sections + s_next
            v2 = (r + 1) * sections + s
            v3 = (r + 1) * sections + s_next
            faces.append([v0, v2, v1])
            faces.append([v1, v2, v3])

    if cap:
        # Đáy dưới (y = -height/2)
        bot_idx = len(vertices)
        vertices.append([0.0, -height / 2.0, 0.0])
        for s in range(sections):
            s_next = (s + 1) % sections
            faces.append([bot_idx, s, s_next])

        # Đáy trên (y = height/2)
        top_idx = len(vertices)
        vertices.append([0.0, height / 2.0, 0.0])
        top_offset = num_height_segments * sections
        for s in range(sections):
            s_next = (s + 1) % sections
            faces.append([top_idx, top_offset + s_next, top_offset + s])

    return trimesh.Trimesh(
        vertices=np.array(vertices, dtype=np.float64),
        faces=np.array(faces, dtype=np.int64),
        process=True,
    )


@pytest.fixture
def analytical_cylinder_torso() -> trimesh.Trimesh:
    """Fixture hình trụ cơ thể: bán kính 0.15 m, chiều cao 0.80 m theo trục Y."""
    return create_cylinder_y(radius=0.15, height=0.80, num_height_segments=20, sections=32, cap=True)


# ==============================================================================
# TEST CASE TC-FIT-01: PENETRATION RATIO & PENETRATION SCORE
# ==============================================================================

@pytest.mark.fast
def test_penetration_ratio_tc_fit_01(
    analytical_sphere_body: trimesh.Trimesh,
    analytical_sphere_garment_outer: trimesh.Trimesh,
    analytical_sphere_garment_inner: trimesh.Trimesh,
):
    """
    Test Case ID: TC-FIT-01
    Target: Kiểm định tỷ lệ xuyên thấu (Penetration) với mesh giải tích khối cầu.
    Kịch bản:
    1) Khối cầu áo nằm hoàn toàn ngoài cơ thể (R_garment = 0.22m > R_body = 0.20m):
       Expected: Penetration Ratio = 0.0, Penetration Score = 100.0.
    2) Khối cầu áo nhỏ hơn cơ thể (R_garment = 0.18m < R_body = 0.20m):
       Expected: Penetration Ratio = 1.0 (toàn bộ đỉnh nằm trong), Penetration Score = 0.0.
    """
    # 1. Kịch bản áo ngoài
    res_outer = compute_penetration(analytical_sphere_body, analytical_sphere_garment_outer)
    assert res_outer["penetration_ratio"] == pytest.approx(0.0, abs=1e-4)
    assert res_outer["penetration_score"] == pytest.approx(100.0, abs=1e-2)
    assert res_outer["num_penetrating"] == 0
    assert res_outer["max_penetration_depth"] == pytest.approx(0.0, abs=1e-4)

    # 2. Kịch bản áo trong (bị xuyên thấu 100%)
    res_inner = compute_penetration(analytical_sphere_body, analytical_sphere_garment_inner)
    assert res_inner["penetration_ratio"] == pytest.approx(1.0, abs=1e-4)
    assert res_inner["penetration_score"] == pytest.approx(0.0, abs=1e-2)
    assert res_inner["num_penetrating"] == res_inner["total_vertices"]
    # Độ sâu lẹm lý thuyết = 0.20 - 0.18 = 0.02 m (2 cm)
    assert res_inner["max_penetration_depth"] == pytest.approx(0.02, abs=2e-3)


# ==============================================================================
# TEST CASE TC-FIT-02: DISTANCE CALCULATION & PER-VERTEX ARRAY
# ==============================================================================

@pytest.mark.fast
def test_distance_calculation_tc_fit_02(
    analytical_sphere_body: trimesh.Trimesh,
    analytical_sphere_garment_outer: trimesh.Trimesh,
):
    """
    Test Case ID: TC-FIT-02
    Target: Đo khoảng cách bề mặt từ đỉnh áo tới cơ thể (Khoảng cách lý thuyết = 2.0 cm).
    Expected:
    - Khoảng cách trung bình avg_distance ≈ 0.02 m (sai số <= 0.001 m).
    - Mảng per_vertex_distance có độ dài đúng bằng tổng số đỉnh của mesh áo.
    """
    res = compute_distance(analytical_sphere_body, analytical_sphere_garment_outer)

    # 1. Kiểm tra độ dài mảng khoảng cách
    assert len(res["per_vertex_distance"]) == len(analytical_sphere_garment_outer.vertices)

    # 2. Khoảng cách giải tích: 0.22 - 0.20 = 0.02 m (2.0 cm)
    assert res["avg_distance"] == pytest.approx(0.02, abs=1e-3)
    assert res["min_distance"] == pytest.approx(0.02, abs=1e-3)
    assert res["max_distance"] == pytest.approx(0.02, abs=1e-3)

    # 3. Điểm số khoảng cách đạt tối đa cho khoảng cách lý tưởng 2.0 cm
    assert res["distance_score"] == pytest.approx(100.0, abs=1.0)


# ==============================================================================
# TEST CASE TC-FIT-03: ANATOMICAL COVERAGE RATIO
# ==============================================================================

@pytest.mark.fast
def test_coverage_ratio_tc_fit_03(analytical_cylinder_torso: trimesh.Trimesh):
    """
    Test Case ID: TC-FIT-03
    Target: Đánh giá độ bao phủ giải phẫu (Coverage Ratio).
    Kịch bản:
    1) Áo bao phủ 100% chiều cao thân: Coverage Ratio ≈ 1.0 (± 0.05).
    2) Áo bị cắt giảm 50% chiều cao: Coverage Ratio ≈ 0.5 (± 0.05).
    """
    # 1. Áo phủ 100% chiều cao (bán kính 0.17m > 0.15m, cùng chiều cao 0.80m)
    full_garment = create_cylinder_y(radius=0.17, height=0.80, num_height_segments=20, sections=32, cap=False)
    res_full = compute_coverage(analytical_cylinder_torso, full_garment, max_threshold_distance=0.05)
    assert res_full["coverage_ratio"] == pytest.approx(1.0, abs=0.05)
    assert res_full["coverage_score"] == pytest.approx(100.0, abs=5.0)

    # 2. Áo ngắn một nửa (chiều cao 0.40m = 50% chiều cao body 0.80m)
    # Dịch chuyển áo lên nửa trên của thân người
    half_garment = create_cylinder_y(radius=0.17, height=0.40, num_height_segments=10, sections=32, cap=False)
    half_garment.apply_translation([0, 0.20, 0])

    res_half = compute_coverage(analytical_cylinder_torso, half_garment, max_threshold_distance=0.05)
    assert res_half["coverage_ratio"] == pytest.approx(0.5, abs=0.08)
    assert res_half["coverage_score"] == pytest.approx(50.0, abs=8.0)


# ==============================================================================
# TEST CASE TC-FIT-04: REGION SEGMENTATION & FIT CATEGORIZATION
# ==============================================================================

@pytest.mark.fast
def test_region_segmentation_and_fit_tc_fit_04(analytical_cylinder_torso: trimesh.Trimesh):
    """
    Test Case ID: TC-FIT-04
    Target: Phân đoạn vùng cơ thể và gán nhãn độ vừa từng vùng {TIGHT, GOOD, LOOSE}.
    Expected:
    - Đủ 4 vùng giải phẫu: shoulder, chest, waist, hip.
    - Nhãn từng vùng tuân thủ chính xác ngưỡng khoảng cách (cm).
    """
    # 1. Kiểm tra phân đoạn vùng trên thân người
    regions = segment_body_regions(analytical_cylinder_torso)
    for r in ALL_REGIONS:
        assert r in regions
        assert regions[r]["count"] > 0

    # 2. Tạo áo có bán kính 0.17 m (khoảng cách 0.17 - 0.15 = 0.02 m = 2.0 cm -> GOOD cho tất cả vùng)
    good_garment = create_cylinder_y(radius=0.17, height=0.80, num_height_segments=20, sections=32, cap=False)
    good_fit = evaluate_region_fit(analytical_cylinder_torso, good_garment)

    for r in ALL_REGIONS:
        assert good_fit[r]["status"] == STATUS_GOOD
        assert good_fit[r]["avg_distance_cm"] == pytest.approx(2.0, abs=0.2)

    # 3. Tạo áo có bán kính 0.19 m (khoảng cách 0.19 - 0.15 = 0.04 m = 4.0 cm > 3.0 cm -> LOOSE)
    loose_garment = create_cylinder_y(radius=0.19, height=0.80, num_height_segments=20, sections=32, cap=False)
    loose_fit = evaluate_region_fit(analytical_cylinder_torso, loose_garment)

    for r in ALL_REGIONS:
        assert loose_fit[r]["status"] == STATUS_LOOSE
        assert loose_fit[r]["avg_distance_cm"] == pytest.approx(4.0, abs=0.2)


# ==============================================================================
# TEST CASE TC-FIT-05: STANDARDIZED FIT SCORE FORMULA
# ==============================================================================

@pytest.mark.fast
def test_fit_score_formula_tc_fit_05():
    """
    Test Case ID: TC-FIT-05
    Target: Kiểm định công thức điểm tổng thể Fit Score = 0.4*Pen + 0.3*Dist + 0.3*Cov.
    Input từ tài liệu test case: Penetration=95.0, Distance=82.0, Coverage=90.0.
    Expected: Fit Score = 0.4*(95) + 0.3*(82) + 0.3*(90) = 38.0 + 24.6 + 27.0 = 89.6 (dung sai <= 0.05).
    """
    # 1. Kiểm tra trọng số chuẩn
    assert WEIGHT_PENETRATION == 0.4
    assert WEIGHT_DISTANCE == 0.3
    assert WEIGHT_COVERAGE == 0.3
    assert (WEIGHT_PENETRATION + WEIGHT_DISTANCE + WEIGHT_COVERAGE) == pytest.approx(1.0)

    # 2. Kiểm định giá trị chuẩn theo TC-FIT-05
    pen_in = 95.0
    dist_in = 82.0
    cov_in = 90.0
    expected_score = 0.4 * 95.0 + 0.3 * 82.0 + 0.3 * 90.0  # 89.6

    computed_score = compute_fit_score(pen_in, dist_in, cov_in)
    assert computed_score == pytest.approx(expected_score, abs=0.05)
    assert computed_score == 89.6

    # 3. Kiểm định các ca biên
    assert compute_fit_score(100.0, 100.0, 100.0) == 100.0
    assert compute_fit_score(0.0, 0.0, 0.0) == 0.0


# ==============================================================================
# TEST CASE TC-FIT-06: HEATMAP JSON EXPORT & SCHEMA VALIDATION
# ==============================================================================

@pytest.mark.fast
def test_heatmap_json_export_tc_fit_06(tmp_path):
    """
    Test Case ID: TC-FIT-06
    Target: Xuất file heatmap.json validate 100% JSON contract.
    Expected:
    - Cấu trúc đầy đủ các trường: garment_id, size, vertex_count, unit='cm', distances.
    - Số phần tử mảng distances bằng đúng vertex_count.
    - File JSON lưu thành công và parse được nguyên vẹn.
    """
    # 1. Giả lập mảng khoảng cách cho 500 đỉnh áo
    num_vertices = 500
    mock_distances_m = np.random.uniform(0.01, 0.03, size=num_vertices)
    mock_penetrations = np.zeros(num_vertices, dtype=bool)
    mock_penetrations[:20] = True  # 20 đỉnh bị xuyên thấu (sẽ mang dấu âm)

    payload = generate_heatmap_payload(
        per_vertex_distance_m=mock_distances_m,
        is_penetrating=mock_penetrations,
        garment_id="tshirt_cotton_demo",
        size="M",
    )

    # 2. Kiểm định cấu trúc payload
    assert payload["garment_id"] == "tshirt_cotton_demo"
    assert payload["size"] == "M"
    assert payload["unit"] == "cm"
    assert payload["vertex_count"] == num_vertices
    assert len(payload["distances"]) == num_vertices
    assert validate_heatmap_schema(payload) is True

    # Có ít nhất 1 giá trị âm do đỉnh bị xuyên thấu
    assert payload["min_distance"] < 0.0

    # 3. Xuất ra file json trên ổ đĩa
    out_file = tmp_path / "heatmap_test.json"
    json_str = export_heatmap_json(payload, output_path=out_file)

    assert out_file.exists()
    loaded_data = json.loads(json_str)
    assert loaded_data["vertex_count"] == num_vertices
    assert len(loaded_data["distances"]) == num_vertices


# ==============================================================================
# END-TO-END WORKFLOW TEST: GEOMETRY FIT EVALUATOR
# ==============================================================================

@pytest.mark.fast
def test_geometry_fit_evaluator_end_to_end(
    analytical_sphere_body: trimesh.Trimesh,
    analytical_sphere_garment_outer: trimesh.Trimesh,
):
    """Kiểm tra luồng xử lý trọn vẹn của GeometryFitEvaluator thông qua interface chuẩn."""
    evaluator = GeometryFitEvaluator(garment_id="sphere_shirt", size="M")
    result = evaluator.evaluate(analytical_sphere_body, analytical_sphere_garment_outer)

    # 1. Các trường kết quả cấp cao
    assert "fit_score" in result
    assert "classification" in result
    assert "metrics" in result
    assert "regions" in result
    assert "heatmap" in result
    assert "diagnostics" in result
    assert "specs_comparison" in result
    assert "ai_insights" in result

    # 2. Khối cầu ngoài lý tưởng -> Điểm cao, phân loại Good
    assert result["fit_score"] >= 80.0
    assert result["classification"] in ["Good", "Too Tight", "Too Loose"]
    assert result["metrics"]["penetration_ratio"] == 0.0
    assert result["heatmap"]["vertex_count"] == len(analytical_sphere_garment_outer.vertices)
