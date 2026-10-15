"""Training Script for Production Random Forest Models (Task AI-04).

Trains RandomForestRegressor (Fit Score) and RandomForestClassifier (Fit Class)
on 15 engineered anthropometric & garment interaction features.
Evaluates on independent Test Set against TC-AI-04 criteria:
- MAE <= 5.0 points for Fit Score
- Macro F1 >= 0.75 for Fit Classification
Exports production weights to ai/models/weights/fit_predictor_rf.joblib.
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
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from ai.dataset.labeling.fit_labeler import FIT_CLASSES, assign_fit_labels
from ai.dataset.preprocessing.feature_engineer import (
    ALL_FEATURE_COLS,
    extract_fit_features,
)
from ai.dataset.split import DEFAULT_SPLIT_DIR, run_pipeline

WEIGHTS_DIR = PROJECT_ROOT / "ai" / "models" / "weights"


def evaluate_rf_models(
    rf_reg: RandomForestRegressor,
    rf_clf: RandomForestClassifier,
    X_test: pd.DataFrame,
    y_test_class: pd.Series,
    y_test_score: pd.Series,
) -> Dict[str, Any]:
    """Đánh giá toàn diện cả 2 mô hình trên tập kiểm thử độc lập."""
    # 1. Hồi quy Fit Score
    y_pred_score = rf_reg.predict(X_test)
    mae = float(mean_absolute_error(y_test_score, y_pred_score))
    rmse = float(np.sqrt(mean_squared_error(y_test_score, y_pred_score)))
    r2 = float(r2_score(y_test_score, y_pred_score))

    # 2. Phân loại Fit Class
    y_pred_class = rf_clf.predict(X_test)
    acc = float(accuracy_score(y_test_class, y_pred_class))
    macro_f1 = float(f1_score(y_test_class, y_pred_class, average="macro", zero_division=0))

    print("\n" + "=" * 65)
    print("      KẾT QUẢ ĐÁNH GIÁ RANDOM FOREST TRÊN TEST SET ĐỘC LẬP      ")
    print("=" * 65)
    print("[*] HỒI QUY FIT SCORE:")
    print(f"    - MAE            : {mae:.3f} điểm (Yêu cầu TC-AI-04: <= 5.0) -> {'ĐẠT XUẤT SẮC' if mae <= 5.0 else 'CHƯA ĐẠT'}")
    print(f"    - RMSE           : {rmse:.3f} điểm")
    print(f"    - R^2 Score      : {r2:.4f}")

    print("\n[*] PHÂN LOẠI FIT CLASS:")
    print(f"    - Accuracy       : {acc * 100:.2f}%")
    print(f"    - Macro F1-Score : {macro_f1:.4f} (Yêu cầu TC-AI-04: >= 0.75) -> {'ĐẠT XUẤT SẮC' if macro_f1 >= 0.75 else 'CHƯA ĐẠT'}")

    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test_class, y_pred_class, labels=FIT_CLASSES)
    cm_df = pd.DataFrame(
        cm,
        index=[f"True_{c}" for c in FIT_CLASSES],
        columns=[f"Pred_{c}" for c in FIT_CLASSES],
    )
    print(cm_df)

    return {
        "MAE": round(mae, 3),
        "RMSE": round(rmse, 3),
        "R2": round(r2, 4),
        "Accuracy": round(acc * 100, 2),
        "Macro_F1": round(macro_f1, 4),
    }


def main() -> None:
    print("=" * 65)
    print("        HUẤN LUYỆN MÔ HÌNH CHÍNH (RANDOM FOREST V1) - M4        ")
    print("=" * 65)

    train_path = DEFAULT_SPLIT_DIR / "train.csv"
    val_path = DEFAULT_SPLIT_DIR / "val.csv"
    test_path = DEFAULT_SPLIT_DIR / "test.csv"

    if not (train_path.exists() and test_path.exists()):
        print("[!] Chưa tìm thấy splits, tự động chạy pipeline chia dữ liệu...")
        run_pipeline()

    print(f"[*] Nạp dữ liệu splits từ: {DEFAULT_SPLIT_DIR}")
    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)
    test_df = pd.read_csv(test_path)

    # Gán nhãn Fit nếu chưa có
    if "fit_class" not in train_df.columns:
        print("[*] Gán nhãn Fit Labeling...")
        train_df = assign_fit_labels(train_df)
        val_df = assign_fit_labels(val_df)
        test_df = assign_fit_labels(test_df)

    # Trích xuất 15 đặc trưng chuyên sâu
    print("[*] Trích xuất 15 đặc trưng nhân trắc học & tương tác...")
    train_feat = extract_fit_features(train_df)
    test_feat = extract_fit_features(test_df)

    X_train = train_feat[ALL_FEATURE_COLS]
    y_train_class = train_feat["fit_class"]
    y_train_score = train_feat["fit_score"]

    X_test = test_feat[ALL_FEATURE_COLS]
    y_test_class = test_feat["fit_class"]
    y_test_score = test_feat["fit_score"]

    print(f"[*] Số mẫu Train: {len(X_train):,} | Test: {len(X_test):,}")

    # Huấn luyện Random Forest
    print("\n[*] Đang huấn luyện Random Forest Regressor (Fit Score)...")
    rf_reg = RandomForestRegressor(
        n_estimators=100,
        max_depth=16,
        random_state=42,
        n_jobs=-1,
    )
    rf_reg.fit(X_train, y_train_score)

    print("[*] Đang huấn luyện Random Forest Classifier (Fit Class)...")
    rf_clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=16,
        random_state=42,
        n_jobs=-1,
    )
    rf_clf.fit(X_train, y_train_class)

    # Đánh giá
    metrics = evaluate_rf_models(rf_reg, rf_clf, X_test, y_test_class, y_test_score)

    # Đóng gói và lưu Model Weights
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    model_bundle = {
        "regressor": rf_reg,
        "classifier": rf_clf,
        "feature_cols": ALL_FEATURE_COLS,
        "classes": FIT_CLASSES,
        "metrics": metrics,
    }

    weight_path = WEIGHTS_DIR / "fit_predictor_rf.joblib"
    joblib.dump(model_bundle, weight_path)
    print(f"\n[+] Đã lưu gói trọng số chính thức tại: {weight_path}")


if __name__ == "__main__":
    main()
