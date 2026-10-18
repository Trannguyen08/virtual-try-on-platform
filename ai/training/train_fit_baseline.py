"""Training & Benchmarking Script for Fit Predictor & Classifier Baselines (Task AI-04).

Trains and evaluates 3 baseline levels:
1. Dummy Model (Mean score & Majority class floor)
2. Rule-Based Heuristic (Geometry Fallback)
3. ML Baseline (Ridge Regression + Logistic Regression)
Evaluates on independent Test Set against TC-AI-04 criteria:
- MAE <= 5.0 points for Fit Score
- Macro F1 >= 0.75 for Fit Classification
And exports packaged model weight to ai/models/weights/fit_predictor_baseline.joblib.
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
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from ai.dataset.labeling.fit_labeler import (
    FIT_CLASSES,
    assign_fit_labels,
)
from ai.dataset.split import DEFAULT_SPLIT_DIR, run_pipeline
from ai.models.fit_predictor import (
    FIT_FEATURE_COLUMNS,
    DummyFitPredictor,
    FitPredictor,
    MLFitPredictor,
    RuleBasedFitPredictor,
)

WEIGHTS_DIR = PROJECT_ROOT / "ai" / "models" / "weights"


def evaluate_fit_model(
    model: Any,
    X_test: pd.DataFrame,
    y_test_class: pd.Series,
    y_test_score: pd.Series,
    model_name: str,
) -> Dict[str, Any]:
    """Đánh giá cả 2 tác vụ: Phân loại Fit Class và Hồi quy Fit Score."""
    # 1. Dự đoán
    pred_class = model.predict_class(X_test)
    pred_score = model.predict_score(X_test)

    # 2. Chỉ số bài toán Phân loại (Classification)
    acc = float(accuracy_score(y_test_class, pred_class))
    macro_f1 = float(f1_score(y_test_class, pred_class, average="macro", zero_division=0))

    # 3. Chỉ số bài toán Hồi quy (Regression)
    mae = float(mean_absolute_error(y_test_score, pred_score))
    rmse = float(np.sqrt(mean_squared_error(y_test_score, pred_score)))
    r2 = float(r2_score(y_test_score, pred_score))

    print(f"\n--- [ĐÁNH GIÁ: {model_name}] ---")
    print(f"[*] HỒI QUY FIT SCORE:")
    print(f"    - MAE            : {mae:.2f} điểm (Yêu cầu TC-AI-04: <= 5.0)")
    print(f"    - RMSE           : {rmse:.2f} điểm")
    print(f"    - R^2 Score      : {r2:.4f}")
    print(f"[*] PHÂN LOẠI FIT CLASS:")
    print(f"    - Accuracy       : {acc * 100:.2f}%")
    print(f"    - Macro F1-Score : {macro_f1:.4f} (Yêu cầu TC-AI-04: >= 0.75)")
    print("Confusion Matrix:")
    cm = confusion_matrix(y_test_class, pred_class, labels=FIT_CLASSES)
    cm_df = pd.DataFrame(
        cm,
        index=[f"True_{c}" for c in FIT_CLASSES],
        columns=[f"Pred_{c}" for c in FIT_CLASSES],
    )
    print(cm_df)

    return {
        "Model": model_name,
        "MAE (Score)": round(mae, 2),
        "RMSE (Score)": round(rmse, 2),
        "R2 Score": round(r2, 4),
        "Accuracy (%)": round(acc * 100, 2),
        "Macro F1": round(macro_f1, 4),
    }


def main() -> None:
    print("=" * 70)
    print("       HUẤN LUYỆN & THIẾT LẬP MỐC BASELINE (FIT PREDICTOR & CLASSIFIER)       ")
    print("=" * 70)

    train_path = DEFAULT_SPLIT_DIR / "train.csv"
    val_path = DEFAULT_SPLIT_DIR / "val.csv"
    test_path = DEFAULT_SPLIT_DIR / "test.csv"

    if not (train_path.exists() and test_path.exists()):
        print("[!] Chưa tìm thấy tập splits, tự động chạy split pipeline...")
        run_pipeline()

    print("[*] Nạp dữ liệu splits...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    # Gán nhãn Fit nếu chưa có
    if "fit_class" not in train_df.columns or "fit_score" not in train_df.columns:
        print("[*] Áp dụng logic gán nhãn Fit Labeling (fit_labeler.py)...")
        train_df = assign_fit_labels(train_df)
        test_df = assign_fit_labels(test_df)

    # Chuẩn bị đặc trưng
    X_train = train_df[FIT_FEATURE_COLUMNS]
    y_train_class = train_df["fit_class"]
    y_train_score = train_df["fit_score"]

    X_test = test_df[FIT_FEATURE_COLUMNS]
    y_test_class = test_df["fit_class"]
    y_test_score = test_df["fit_score"]

    print(f"[*] Số mẫu Train: {len(X_train):,} | Test: {len(X_test):,}")

    benchmark_results = []

    # 1. Baseline 1: Dummy Predictor
    print("\n[1/3] Đang đánh giá Baseline 1: Dummy Predictor...")
    dummy = DummyFitPredictor()
    dummy.fit(X_train, y_train_class, y_train_score)
    res_dummy = evaluate_fit_model(dummy, X_test, y_test_class, y_test_score, "Dummy Floor")
    benchmark_results.append(res_dummy)

    # 2. Baseline 2: Rule-Based Geometry Heuristic
    print("\n[2/3] Đang đánh giá Baseline 2: Rule-Based Heuristic...")
    rule_based = RuleBasedFitPredictor()
    res_rule = evaluate_fit_model(rule_based, X_test, y_test_class, y_test_score, "Rule-Based Heuristic")
    benchmark_results.append(res_rule)

    # 3. Baseline 3: Simple ML Baseline (Ridge + Logistic Regression)
    print("\n[3/3] Đang huấn luyện & đánh giá Baseline 3: Simple ML Pipeline...")
    ml_model = MLFitPredictor(random_state=42)
    ml_model.fit(X_train, y_train_class, y_train_score)
    res_ml = evaluate_fit_model(ml_model, X_test, y_test_class, y_test_score, "ML Baseline (Ridge + LogReg)")
    benchmark_results.append(res_ml)

    # Bảng tổng kết
    print("\n" + "=" * 70)
    print("                     BẢNG TỔNG KẾT BENCHMARK BASELINES (TC-AI-04)                     ")
    print("=" * 70)
    summary_df = pd.DataFrame(benchmark_results)
    print(summary_df.to_string(index=False))

    # Đóng gói và lưu model weights
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    unified_wrapper = FitPredictor(model_type="ml_baseline")
    unified_wrapper.fit(X_train, y_train_class, y_train_score)

    weight_path = WEIGHTS_DIR / "fit_predictor_baseline.joblib"
    joblib.dump(unified_wrapper, weight_path)
    print(f"\n[+] Đã lưu Unified Model FitPredictor tại: {weight_path}")

    # Kiểm tra suy luận mẫu
    sample_res = unified_wrapper.predict_single({
        "body_bust": 95.0,
        "body_height": 172.0,
        "body_hips": 98.0,
        "body_waist": 80.0,
        "garment_bust": 101.0,
        "garment_length": 68.0,
    })
    print(f"[+] Thử nghiệm suy luận mẫu: {sample_res}")


if __name__ == "__main__":
    main()
