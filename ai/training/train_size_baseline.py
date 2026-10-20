"""Training & Benchmarking Script for Size Recommendation Baselines.

Trains and evaluates 3 baseline models:
1. Dummy Classifier (Majority Class Floor)
2. Rule-Based Heuristic (Geometry Fallback)
3. Logistic Regression (ML Baseline)
on the independent Test Set (created via Anti-Leakage GroupShuffleSplit).
"""

import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score, f1_score, precision_score, recall_score, confusion_matrix

from ai.dataset.labeling.size_labeler import SIZE_ORDER
from ai.dataset.split import DEFAULT_SPLIT_DIR, run_pipeline
from ai.models.size_recommender import (
    FEATURE_COLUMNS,
    DummySizeRecommender,
    MLSizeRecommender,
    RuleBasedSizeRecommender,
    SizeRecommender,
)

WEIGHTS_DIR = PROJECT_ROOT / "ai" / "models" / "weights"


def evaluate_model(model: Any, X_test: pd.DataFrame, y_test: pd.Series, model_name: str) -> Dict[str, float]:
    """Đánh giá mô hình trên tập kiểm thử độc lập (Test Set)."""
    y_pred = model.predict(X_test)
    
    acc = float(accuracy_score(y_test, y_pred))
    macro_f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
    macro_prec = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
    macro_rec = float(recall_score(y_test, y_pred, average="macro", zero_division=0))

    # Tính tỷ lệ dự đoán sai lệch > 1 size (Severe Size Error - TC-AI-02)
    size_to_idx = {sz: i for i, sz in enumerate(SIZE_ORDER)}
    y_true_indices = np.array([size_to_idx.get(sz, 0) for sz in y_test])
    y_pred_indices = np.array([size_to_idx.get(sz, 0) for sz in y_pred])
    severe_errors = np.abs(y_true_indices - y_pred_indices) > 1
    severe_ratio = float(np.mean(severe_errors) * 100)

    print(f"\n--- [ĐÁNH GIÁ: {model_name}] ---")
    print(f"[*] Accuracy               : {acc * 100:.2f}%")
    print(f"[*] Macro F1-Score         : {macro_f1:.4f}")
    print(f"[*] Macro Precision        : {macro_prec:.4f}")
    print(f"[*] Macro Recall           : {macro_rec:.4f}")
    print(f"[*] Sai lệch > 1 Size      : {severe_ratio:.2f}% (Yêu cầu TC-AI-02: <= 2.0%)")
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred, labels=SIZE_ORDER)
    cm_df = pd.DataFrame(cm, index=[f"True_{s}" for s in SIZE_ORDER], columns=[f"Pred_{s}" for s in SIZE_ORDER])
    print(cm_df)

    return {
        "Model": model_name,
        "Accuracy (%)": round(acc * 100, 2),
        "Macro F1": round(macro_f1, 4),
        "Macro Precision": round(macro_prec, 4),
        "Macro Recall": round(macro_rec, 4),
        "Severe Error (%)": round(severe_ratio, 2),
    }


def main() -> None:
    print("=" * 70)
    print("       HUẤN LUYỆN & THIẾT LẬP MỐC BASELINE (SIZE RECOMMENDATION)       ")
    print("=" * 70)

    train_path = DEFAULT_SPLIT_DIR / "train.csv"
    val_path = DEFAULT_SPLIT_DIR / "val.csv"
    test_path = DEFAULT_SPLIT_DIR / "test.csv"

    # Kiểm tra nếu chưa chia split thì tự động kích hoạt pipeline chia
    if not (train_path.exists() and test_path.exists()):
        print("[!] Chưa tìm thấy tập splits, tự động chạy split pipeline...")
        train_df, val_df, test_df = run_pipeline()
    else:
        print("[*] Nạp dữ liệu các tập từ đĩa:")
        train_df = pd.read_csv(train_path)
        val_df = pd.read_csv(val_path)
        test_df = pd.read_csv(test_path)
        print(f"    Train: {len(train_df):,} | Val: {len(val_df):,} | Test: {len(test_df):,}")

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df["size_label"]

    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df["size_label"]

    results = []

    # 1. Huấn luyện Baseline 1: Dummy Classifier
    print("\n[1/3] Đang đánh giá Baseline 1: Dummy Classifier (Majority Class)...")
    dummy = DummySizeRecommender(strategy="most_frequent")
    dummy.fit(X_train, y_train)
    res_dummy = evaluate_model(dummy, X_test, y_test, "Baseline 1: Dummy (Floor)")
    results.append(res_dummy)

    # 2. Đánh giá Baseline 2: Rule-Based Heuristic (Geometry Fallback)
    print("\n[2/3] Đang đánh giá Baseline 2: Rule-Based Heuristic (Geometry Fallback)...")
    rule_model = RuleBasedSizeRecommender()
    rule_model.fit(X_train, y_train)
    res_rule = evaluate_model(rule_model, X_test, y_test, "Baseline 2: Rule-Based (Fallback)")
    results.append(res_rule)

    # 3. Huấn luyện Baseline 3: Logistic Regression
    print("\n[3/3] Đang huấn luyện Baseline 3: Logistic Regression...")
    ml_model = MLSizeRecommender(model_type="logistic_regression", random_state=42)
    ml_model.fit(X_train, y_train)
    res_ml = evaluate_model(ml_model, X_test, y_test, "Baseline 3: Logistic Regression")
    results.append(res_ml)

    # 4. Đóng gói mô hình chính thức và lưu weights
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    unified_recommender = SizeRecommender(model_type="logistic_regression")
    unified_recommender.fit(X_train, y_train)

    model_save_path = WEIGHTS_DIR / "size_recommender_baseline.joblib"
    joblib.dump(unified_recommender, model_save_path)
    print(f"\n[OK] Đã đóng gói và lưu mô hình Baseline vào: {model_save_path}")

    # Bảng tổng kết Benchmark
    print("\n" + "=" * 70)
    print("                    BẢNG TỔNG KẾT BENCHMARK BASELINES                 ")
    print("=" * 70)
    summary_df = pd.DataFrame(results)
    print(summary_df.to_string(index=False))
    print("=" * 70)

    # Đối chiếu Acceptance Criteria (TC-AI-02)
    ml_acc = res_ml["Accuracy (%)"]
    ml_severe = res_ml["Severe Error (%)"]
    is_tc_ai_02_pass = (ml_acc >= 85.0) and (ml_severe <= 2.0)

    if is_tc_ai_02_pass:
        print(f"\n[PASS] Mô hình đạt chuẩn Acceptance Criteria TC-AI-02 (Accuracy >= 85% & Sai lệch > 1 Size <= 2%).")
    else:
        print(f"\n[WARN] Cần cải thiện thêm ở các mô hình nâng cao (XGBoost / Random Forest).")


if __name__ == "__main__":
    main()
