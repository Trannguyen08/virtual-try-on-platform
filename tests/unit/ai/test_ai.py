"""Unit Test Suite for Module M4 AI Components (Size Recommendation & Fallback).

Covers:
- TC-AI-01: Size Labeling & Distribution Integrity
- TC-AI-02: Size Recommender Models & Metrics
- TC-AI-07: Automatic Fallback to Geometry / Rule-Based on Missing Features
"""

import numpy as np
import pandas as pd
import pytest

from ai.dataset.labeling.size_labeler import (
    SIZE_ORDER,
    assign_size_labels,
    check_size_distribution,
    get_size_from_bust,
)
from ai.dataset.split import split_dataset_by_person
from ai.models.size_recommender import (
    DummySizeRecommender,
    MLSizeRecommender,
    RuleBasedSizeRecommender,
    SizeRecommender,
)


# ==============================================================================
# FIXTURES
# ==============================================================================
@pytest.fixture
def mock_dataset() -> pd.DataFrame:
    """Tạo tập dữ liệu mock nhỏ đại diện cho 30 mẫu từ 6 người mẫu khác nhau."""
    np.random.seed(42)
    rows = []
    # 6 người mẫu, mỗi người mặc 5 áo
    for p_id in range(1, 7):
        p_path = f"images/person/person_{p_id:02d}.jpg"
        base_bust = 85.0 + (p_id - 1) * 7.0  # Tạo giải từ 85cm đến 120cm
        base_height = 160.0 + p_id * 3.0
        base_hips = 90.0 + p_id * 4.0
        base_waist = 70.0 + p_id * 5.0

        for c_id in range(1, 6):
            rows.append({
                "id": f"fit_{p_id}_{c_id}",
                "person_path": p_path,
                "cloth_path": f"images/cloth/cloth_{c_id:02d}.jpg",
                "body_bust": base_bust,
                "body_height": base_height,
                "body_hips": base_hips,
                "body_waist": base_waist,
            })

    return pd.DataFrame(rows)


# ==============================================================================
# 1. TC-AI-01: SIZE LABELING TESTS
# ==============================================================================
@pytest.mark.fast
def test_get_size_from_bust_boundaries():
    """Kiểm tra độ chính xác phân loại size tại các điểm biên."""
    assert get_size_from_bust(88.0) == "S"
    assert get_size_from_bust(93.99) == "S"
    assert get_size_from_bust(94.0) == "M"
    assert get_size_from_bust(100.0) == "M"
    assert get_size_from_bust(103.99) == "M"
    assert get_size_from_bust(104.0) == "L"
    assert get_size_from_bust(110.0) == "L"
    assert get_size_from_bust(113.99) == "L"
    assert get_size_from_bust(114.0) == "XL"
    assert get_size_from_bust(135.0) == "XL"


@pytest.mark.fast
def test_get_size_from_bust_invalid_input():
    """Kiểm tra xử lý lỗi khi số đo ngực là NaN hoặc vô hạn."""
    with pytest.raises(ValueError):
        get_size_from_bust(np.nan)
    with pytest.raises(ValueError):
        get_size_from_bust(float("inf"))


@pytest.mark.fast
def test_assign_size_labels_dataframe(mock_dataset):
    """Kiểm tra gán nhãn hàng loạt cho DataFrame."""
    labeled_df = assign_size_labels(mock_dataset)
    assert "size_label" in labeled_df.columns
    assert len(labeled_df) == len(mock_dataset)
    assert set(labeled_df["size_label"].unique()).issubset(set(SIZE_ORDER))


@pytest.mark.fast
def test_check_size_distribution():
    """Kiểm tra phát hiện mất cân bằng phân phối size."""
    df_balanced = pd.DataFrame({"size_label": ["S"] * 25 + ["M"] * 25 + ["L"] * 25 + ["XL"] * 25})
    res_balanced = check_size_distribution(df_balanced)
    assert res_balanced["is_valid"] is True
    assert len(res_balanced["warnings"]) == 0

    df_imbalanced = pd.DataFrame({"size_label": ["S"] * 2 + ["M"] * 50 + ["L"] * 30 + ["XL"] * 18})
    res_imbalanced = check_size_distribution(df_imbalanced)
    assert res_imbalanced["is_valid"] is False
    assert any("Lớp 'S'" in w for w in res_imbalanced["warnings"])


# ==============================================================================
# 2. ANTI-LEAKAGE SPLIT TESTS
# ==============================================================================
@pytest.mark.fast
def test_split_dataset_by_person_anti_leakage(mock_dataset):
    """Kiểm tra chia tập dữ liệu chống rò rỉ danh tính người mẫu 100%."""
    labeled_df = assign_size_labels(mock_dataset)
    train_df, val_df, test_df = split_dataset_by_person(
        labeled_df,
        train_ratio=0.50,
        val_ratio=0.25,
        test_ratio=0.25,
        random_state=42,
    )

    train_persons = set(train_df["person_path"])
    val_persons = set(val_df["person_path"])
    test_persons = set(test_df["person_path"])

    # Xác nhận không có bất kỳ giao cắt nào về danh tính
    assert len(train_persons & val_persons) == 0
    assert len(train_persons & test_persons) == 0
    assert len(val_persons & test_persons) == 0
    assert len(train_df) + len(val_df) + len(test_df) == len(mock_dataset)


# ==============================================================================
# 3. TC-AI-02: BASELINE MODELS TESTS
# ==============================================================================
@pytest.mark.fast
def test_rule_based_recommender():
    """Kiểm tra dự đoán của Rule-based Heuristic."""
    recommender = RuleBasedSizeRecommender()
    df_input = pd.DataFrame({
        "body_bust": [90.0, 98.0, 108.0, 120.0],
        "body_height": [165.0, 170.0, 175.0, 180.0],
    })
    preds = recommender.predict(df_input)
    assert list(preds) == ["S", "M", "L", "XL"]

    probs = recommender.predict_proba(df_input)
    assert probs.shape == (4, 4)
    assert np.all(np.max(probs, axis=1) == 1.0)


@pytest.mark.fast
def test_ml_size_recommender_pipeline(mock_dataset):
    """Kiểm tra huấn luyện và suy luận của Logistic Regression Baseline."""
    labeled_df = assign_size_labels(mock_dataset)
    X = labeled_df[["body_bust", "body_height", "body_hips", "body_waist"]]
    y = labeled_df["size_label"]

    ml_model = MLSizeRecommender(model_type="logistic_regression", random_state=42)
    ml_model.fit(X, y)

    preds = ml_model.predict(X)
    assert len(preds) == len(X)
    assert set(preds).issubset(set(SIZE_ORDER))

    probs = ml_model.predict_proba(X)
    assert probs.shape == (len(X), len(SIZE_ORDER))
    assert np.allclose(probs.sum(axis=1), 1.0)


# ==============================================================================
# 4. TC-AI-07: FALLBACK MECHANISM TESTS
# ==============================================================================
@pytest.mark.fast
def test_unified_size_recommender_inference(mock_dataset):
    """Kiểm tra suy luận của wrapper SizeRecommender khi đầy đủ tham số."""
    labeled_df = assign_size_labels(mock_dataset)
    X = labeled_df[["body_bust", "body_height", "body_hips", "body_waist"]]
    y = labeled_df["size_label"]

    recommender = SizeRecommender(model_type="logistic_regression")
    recommender.fit(X, y)

    # Đầy đủ số đo
    result = recommender.recommend_single({
        "body_bust": 99.0,
        "body_height": 169.0,
        "body_hips": 102.0,
        "body_waist": 85.0,
    })

    assert result["recommended_size"] in SIZE_ORDER
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["fallback_used"] is False
    assert result["method"] == "logistic_regression"


@pytest.mark.fast
def test_unified_size_recommender_fallback_on_missing_features():
    """Kiểm tra tự động fallback an toàn (TC-AI-07) khi thiếu đặc trưng."""
    recommender = SizeRecommender(model_type="logistic_regression")
    # Không gọi fit, chỉ có body_bust -> Fallback sang Rule-based
    result = recommender.recommend_single({
        "body_bust": 91.0,
    })

    assert result["recommended_size"] == "S"
    assert result["fallback_used"] is True
    assert result["method"] == "rule_based_fallback"


@pytest.mark.fast
def test_unified_size_recommender_emergency_fallback_empty():
    """Kiểm tra fallback khẩn cấp khi dict rỗng, không crash ứng dụng (Zero Crash)."""
    recommender = SizeRecommender(model_type="logistic_regression")
    result = recommender.recommend_single({})

    assert result["recommended_size"] == "M"
    assert result["fallback_used"] is True
    assert result["method"] == "emergency_default"
