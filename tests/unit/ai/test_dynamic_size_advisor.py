"""Unit Test Suite cho Mô hình Khuyến nghị Kích cỡ Động (DynamicSizeAdvisor).

Kiểm tra toàn diện 4 trụ cột của Dynamic Size Advisor:
1. AnthropometricEstimator: Chuyển đổi Chiều cao/Cân nặng -> Số đo 4 vòng, tính BMI, và Fall-forward khi có số đo 3D M1.
2. GarmentDimensionPredictor: Dự đoán dải thông số trang phục lý tưởng theo phong cách (Regular, Slim, Oversized).
3. DynamicSizeMatcher: Khớp kích cỡ linh hoạt với bất kỳ bảng size nào (kể cả bảng size số 1, 2, 3 của Local Brand).
4. DynamicSizeAdvisor: Luồng tích hợp End-to-End toàn diện.
"""

import pytest
import numpy as np

from ai.models.dynamic_size_advisor import (
    AnthropometricEstimator,
    GarmentDimensionPredictor,
    DynamicSizeMatcher,
    DynamicSizeAdvisor,
    DEFAULT_GARMENT_SIZE_CHART,
)


# ==============================================================================
# 1. ANTHROPOMETRIC ESTIMATOR TESTS
# ==============================================================================
@pytest.mark.fast
def test_anthropometric_estimator_bmi_calculation():
    """Kiểm tra tính toán chỉ số BMI và phân loại thể trạng."""
    bmi_normal, cat_normal = AnthropometricEstimator.compute_bmi(height_cm=170.0, weight_kg=65.0)
    assert 22.0 <= bmi_normal <= 23.0
    assert "Cân đối" in cat_normal or "Normal" in cat_normal

    bmi_thin, cat_thin = AnthropometricEstimator.compute_bmi(height_cm=175.0, weight_kg=50.0)
    assert bmi_thin < 18.5
    assert "Gầy" in cat_thin

    bmi_over, cat_over = AnthropometricEstimator.compute_bmi(height_cm=165.0, weight_kg=80.0)
    assert bmi_over > 25.0
    assert "Plus-size" in cat_over or "Đậm người" in cat_over


@pytest.mark.fast
def test_anthropometric_estimator_gender_differences():
    """Kiểm tra ước lượng số đo có sự phân hóa theo giới tính."""
    male_profile = AnthropometricEstimator.estimate_measurements(
        height_cm=170.0,
        weight_kg=65.0,
        gender="male",
    )
    female_profile = AnthropometricEstimator.estimate_measurements(
        height_cm=170.0,
        weight_kg=65.0,
        gender="female",
    )

    # Nam giới thường có vai và ngực rộng hơn ở cùng chiều cao/cân nặng
    assert male_profile["shoulder"] > female_profile["shoulder"]
    # Nữ giới có tỷ lệ hông trên eo lớn hơn
    female_hip_waist_ratio = female_profile["hip"] / female_profile["waist"]
    male_hip_waist_ratio = male_profile["hip"] / male_profile["waist"]
    assert female_hip_waist_ratio > male_hip_waist_ratio


@pytest.mark.fast
def test_anthropometric_estimator_fall_forward_exact_mesh():
    """Kiểm tra cơ chế Fall-forward: Số đo từ 3D Mesh M1 ghi đè hoàn toàn công thức ước lượng."""
    exact_3d = {
        "bust": 95.0,
        "waist": 78.0,
        "hip": 100.0,
        "shoulder": 43.5,
    }

    profile = AnthropometricEstimator.estimate_measurements(
        height_cm=170.0,
        weight_kg=65.0,
        exact_measurements=exact_3d,
    )

    assert profile["source"] == "exact_3d_mesh"
    assert profile["bust"] == 95.0
    assert profile["waist"] == 78.0
    assert profile["hip"] == 100.0
    assert profile["shoulder"] == 43.5


# ==============================================================================
# 2. GARMENT DIMENSION PREDICTOR TESTS
# ==============================================================================
@pytest.mark.fast
def test_garment_dimension_predictor_regular_fit():
    """Kiểm tra dải thông số áo lý tưởng cho phong cách Regular Fit."""
    body = {"bust": 92.0, "waist": 74.0, "shoulder": 42.0, "height": 170.0}
    target = GarmentDimensionPredictor.predict_target_range(body, fit_preference="regular")

    assert target["fit_preference"] == "regular"
    # Dải ngực áo: 92 + [4.0, 9.0] -> [96.0, 101.0], tối ưu 98.0
    assert target["target_bust_range_cm"]["min"] == pytest.approx(96.0, abs=0.2)
    assert target["target_bust_range_cm"]["optimal"] == pytest.approx(98.0, abs=0.2)
    assert target["target_bust_range_cm"]["max"] == pytest.approx(101.0, abs=0.2)
    assert target["recommended_ease_cm"] == 6.0


@pytest.mark.fast
def test_garment_dimension_predictor_styles_comparison():
    """Kiểm tra sự khác biệt giữa các phong cách Slim Fit, Regular và Oversized."""
    body = {"bust": 92.0, "waist": 74.0, "shoulder": 42.0, "height": 170.0}

    slim = GarmentDimensionPredictor.predict_target_range(body, fit_preference="slim")
    regular = GarmentDimensionPredictor.predict_target_range(body, fit_preference="regular")
    oversized = GarmentDimensionPredictor.predict_target_range(body, fit_preference="oversized")

    # Ngực áo Oversized > Regular > Slim
    assert oversized["target_bust_range_cm"]["optimal"] > regular["target_bust_range_cm"]["optimal"]
    assert regular["target_bust_range_cm"]["optimal"] > slim["target_bust_range_cm"]["optimal"]

    # Độ chênh vai áo Oversized cũng rộng hơn đáng kể (vai trễ)
    assert oversized["target_shoulder_range_cm"]["optimal"] > regular["target_shoulder_range_cm"]["optimal"]


# ==============================================================================
# 3. DYNAMIC SIZE MATCHER TESTS
# ==============================================================================
@pytest.mark.fast
def test_dynamic_size_matcher_standard_tshirt_chart():
    """Kiểm tra khớp kích cỡ với bảng size tiêu chuẩn S, M, L, XL."""
    body = {"bust": 92.0, "waist": 74.0, "shoulder": 42.0}

    res = DynamicSizeMatcher.match_size_chart(
        body_measurements=body,
        size_chart=DEFAULT_GARMENT_SIZE_CHART,
        fit_preference="regular",
    )

    # Áo Size M ngực 98cm -> Ease +6.0cm là lựa chọn hoàn hảo
    assert res["recommended_size"] == "M"
    assert res["actual_bust_ease_cm"] == 6.0
    assert res["confidence"] >= 0.90
    assert len(res["all_sizes_analysis"]) == 4

    # Kiểm tra phân tích từng size
    analysis_map = {item["size"]: item for item in res["all_sizes_analysis"]}
    assert analysis_map["S"]["bust_ease_cm"] == -2.0
    assert analysis_map["S"]["is_wearable"] is False  # Chật ngực
    assert analysis_map["M"]["is_recommended"] is True


@pytest.mark.fast
def test_dynamic_size_matcher_non_standard_local_brand_chart():
    """Kiểm tra khớp kích cỡ với bảng size phi tiêu chuẩn (Size 1, Size 2, Size 3 của Local Brand)."""
    local_brand_chart = {
        "Size 1 (Fit gọn)": {"bust": 94.0, "length": 69.0, "shoulder": 43.0},
        "Size 2 (Vừa vặn)": {"bust": 100.0, "length": 72.0, "shoulder": 46.0},
        "Size 3 (Form rộng)": {"bust": 108.0, "length": 75.0, "shoulder": 49.0},
    }

    body = {"bust": 93.0, "waist": 75.0, "shoulder": 42.0}

    # Phong cách Regular (cần ease khoảng +6cm): 93 + 6 = 99 -> Gần Size 2 (ngực 100, ease +7cm) nhất
    res_regular = DynamicSizeMatcher.match_size_chart(
        body_measurements=body,
        size_chart=local_brand_chart,
        fit_preference="regular",
    )
    assert res_regular["recommended_size"] == "Size 2 (Vừa vặn)"
    assert res_regular["actual_bust_ease_cm"] == 7.0

    # Nếu người dùng muốn mặc Streetwear Oversized (cần ease khoảng +14cm): 93 + 14 = 107 -> Chọn Size 3 (108cm)
    res_oversized = DynamicSizeMatcher.match_size_chart(
        body_measurements=body,
        size_chart=local_brand_chart,
        fit_preference="oversized",
    )
    assert res_oversized["recommended_size"] == "Size 3 (Form rộng)"
    assert res_oversized["actual_bust_ease_cm"] == 15.0


# ==============================================================================
# 4. UNIFIED DYNAMIC SIZE ADVISOR END-TO-END TESTS
# ==============================================================================
@pytest.mark.fast
def test_dynamic_size_advisor_end_to_end_cold_start():
    """Kiểm tra kịch bản Cold-Start: Người dùng chỉ nhập Chiều cao 170cm và Cân nặng 65kg."""
    advisor = DynamicSizeAdvisor()
    result = advisor.advise(
        height_cm=170.0,
        weight_kg=65.0,
        gender="male",
        fit_preference="regular",
    )

    assert result["status"] == "success"
    # Kiểm tra hồ sơ vóc dáng ước lượng
    profile = result["body_profile"]
    assert profile["source"] == "anthropometric_estimation"
    assert 88.0 <= profile["bust"] <= 95.0

    # Kiểm tra dải kích thước mục tiêu
    target = result["target_garment_dimension_range"]
    assert target["recommended_ease_cm"] == 6.0

    # Kiểm tra đề xuất cuối cùng
    rec = result["recommendation"]
    assert rec["recommended_size"] in ["S", "M", "L"]
    assert rec["confidence"] > 0.70
    assert "Đề xuất" in rec["reason"]


@pytest.mark.fast
def test_dynamic_size_advisor_end_to_end_with_exact_3d_measurements():
    """Kiểm tra kịch bản đã có kết quả đo 3D từ Module M1 (Ngực 92cm, Eo 74cm)."""
    advisor = DynamicSizeAdvisor()
    exact_3d_body = {
        "bust": 92.0,
        "waist": 74.0,
        "hip": 96.0,
        "shoulder": 42.0,
        "height": 170.0,
    }

    result = advisor.advise(
        height_cm=170.0,
        weight_kg=65.0,
        body_measurements=exact_3d_body,
        fit_preference="regular",
    )

    assert result["body_profile"]["source"] == "exact_3d_mesh"
    assert result["body_profile"]["bust"] == 92.0

    # Với ngực 92.0cm, bảng size tiêu chuẩn bắt buộc phải đề xuất Size M
    assert result["recommendation"]["recommended_size"] == "M"
    assert result["recommendation"]["actual_bust_ease_cm"] == 6.0
    assert result["recommendation"]["confidence"] >= 0.95


@pytest.mark.fast
def test_size_recommender_advise_dynamic_bridge():
    """Kiểm tra gọi DynamicSizeAdvisor thông qua wrapper SizeRecommender."""
    from ai.models.size_recommender import SizeRecommender
    recommender = SizeRecommender()
    res = recommender.advise_dynamic(
        height_cm=170.0,
        weight_kg=65.0,
        fit_preference="oversized",
    )
    assert res["status"] == "success"
    assert res["target_garment_dimension_range"]["fit_preference"] == "oversized"
    assert "recommendation" in res


@pytest.mark.fast
def test_garment_category_shirt_vs_tshirt():
    """Kiểm tra sự khác biệt giữa Áo thun (co giãn) và Áo sơ mi (không co giãn)."""
    advisor = DynamicSizeAdvisor()
    body = {"bust": 92.0, "waist": 74.0, "hip": 96.0, "shoulder": 42.0, "height": 170.0}

    shirt_chart = {
        "Size 38 (S)": {"bust": 94.0, "length": 71.0, "shoulder": 42.0},
        "Size 39 (M)": {"bust": 98.0, "length": 72.0, "shoulder": 44.0},
        "Size 40 (L)": {"bust": 102.0, "length": 74.0, "shoulder": 46.0},
        "Size 41 (XL)": {"bust": 108.0, "length": 76.0, "shoulder": 48.0},
    }

    # Với Áo sơ mi: Ease +2.0cm (Size 38) bị coi là Too Tight do vải dệt thoi không co giãn
    res_shirt = advisor.advise(
        body_measurements=body,
        size_chart=shirt_chart,
        fit_preference="regular",
        garment_category="shirt",
    )
    analysis = {item["size"]: item for item in res_shirt["recommendation"]["all_sizes_analysis"]}
    assert analysis["Size 38 (S)"]["is_wearable"] is False
    assert res_shirt["recommendation"]["recommended_size"] in ["Size 39 (M)", "Size 40 (L)"]

    # Với Áo thun: Ease +2.0cm (Size S) là Slim Fit hoàn toàn mặc được
    tshirt_chart = {
        "S": {"bust": 94.0, "length": 68.0, "shoulder": 42.0},
        "M": {"bust": 98.0, "length": 70.0, "shoulder": 44.0},
    }
    res_tshirt = advisor.advise(
        body_measurements=body,
        size_chart=tshirt_chart,
        fit_preference="slim",
        garment_category="tshirt",
    )
    tshirt_analysis = {item["size"]: item for item in res_tshirt["recommendation"]["all_sizes_analysis"]}
    assert tshirt_analysis["S"]["is_wearable"] is True


