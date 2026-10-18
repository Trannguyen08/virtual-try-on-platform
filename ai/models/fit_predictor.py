"""Fit Predictor Baseline Models for Module M4 (Task AI-04).

Provides 3 baseline levels for simultaneous Fit Score (Regression) and Fit Class (Classification):
1. DummyFitPredictor (Floor threshold / Mean score & Majority class)
2. RuleBasedFitPredictor (Analytical Geometry Heuristic / Core Fallback - TC-AI-07)
3. MLFitPredictor (Ridge Regression & Logistic Regression with RobustScaler)
And a unified FitPredictor wrapper with automatic fallback capability (Zero Crash).
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

from ai.dataset.labeling.fit_labeler import (
    FIT_CLASSES,
    compute_reference_fit_score,
    get_fit_class_from_ease,
)
from ai.dataset.preprocessing.feature_engineer import (
    ALL_FEATURE_COLS,
    extract_fit_features_single,
)

FIT_FEATURE_COLUMNS: List[str] = [
    "body_bust",
    "body_height",
    "body_hips",
    "body_waist",
    "garment_bust",
    "garment_length",
    "bust_diff",
]


class RuleBasedFitPredictor:
    """Baseline 2: Hệ thống dự đoán độ vừa dựa trên công thức hình học (Rule-based Heuristic).

    Đóng vai trò là hệ thống đối chứng vật lý và cơ chế Fallback (TC-AI-07)
    khi AI lỗi, chưa được huấn luyện hoặc thiếu các trường phụ.
    """

    def __init__(self) -> None:
        self.classes_ = np.array(FIT_CLASSES)

    def fit(self, X: Any = None, y: Any = None) -> "RuleBasedFitPredictor":
        """Không cần huấn luyện, tuân thủ interface của scikit-learn."""
        return self

    def _extract_diff(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """Trích xuất hoặc tính toán bust_diff từ dữ liệu đầu vào."""
        if isinstance(X, pd.DataFrame):
            if "bust_diff" in X.columns:
                return X["bust_diff"].values
            elif "garment_bust" in X.columns and "body_bust" in X.columns:
                return (X["garment_bust"] - X["body_bust"]).values
            else:
                return X.iloc[:, 0].values
        else:
            # Nếu là numpy array: cột cuối là bust_diff nếu có >= 7 cột, ngược lại lấy cột 0
            if X.shape[1] >= 7:
                return X[:, 6]
            return X[:, 0]

    def predict_class(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """Dự đoán nhãn phân loại (Too Tight, Good, Too Loose)."""
        diffs = self._extract_diff(X)
        preds = [get_fit_class_from_ease(float(d)) for d in diffs]
        return np.array(preds)

    def predict_score(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """Dự đoán điểm số vừa vặn Fit Score [0, 100]."""
        diffs = self._extract_diff(X)
        scores = [compute_reference_fit_score(float(d)) for d in diffs]
        return np.array(scores)

    def predict(self, X: Union[pd.DataFrame, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        """Trả về cả nhãn phân loại và điểm số hồi quy."""
        return self.predict_class(X), self.predict_score(X)

    def predict_proba(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """Trả về phân phối xác suất one-hot cho nhãn phân loại."""
        preds = self.predict_class(X)
        probs = np.zeros((len(preds), len(self.classes_)))
        for i, pred in enumerate(preds):
            idx = list(self.classes_).index(pred)
            probs[i, idx] = 1.0
        return probs


class DummyFitPredictor:
    """Baseline 1: Ngưỡng sàn tối thiểu (Dummy Regressor Mean & Dummy Classifier Majority)."""

    def __init__(self) -> None:
        self.clf = DummyClassifier(strategy="most_frequent", random_state=42)
        self.reg = DummyRegressor(strategy="mean")
        self.classes_: Optional[np.ndarray] = None

    def fit(
        self,
        X: Any,
        y_class: Any,
        y_score: Any,
    ) -> "DummyFitPredictor":
        self.clf.fit(X, y_class)
        self.reg.fit(X, y_score)
        self.classes_ = self.clf.classes_
        return self

    def predict_class(self, X: Any) -> np.ndarray:
        return self.clf.predict(X)

    def predict_score(self, X: Any) -> np.ndarray:
        return self.reg.predict(X)

    def predict(self, X: Any) -> Tuple[np.ndarray, np.ndarray]:
        return self.predict_class(X), self.predict_score(X)


class MLFitPredictor:
    """Mô hình học máy dự đoán Fit (Hỗ trợ Linear/Ridge và Random Forest v1)."""

    def __init__(self, algorithm: str = "linear", random_state: int = 42) -> None:
        self.algorithm = algorithm
        self.random_state = random_state

        if algorithm == "random_forest":
            self.clf_pipeline = RandomForestClassifier(
                n_estimators=100, max_depth=16, random_state=random_state, n_jobs=-1
            )
            self.reg_pipeline = RandomForestRegressor(
                n_estimators=100, max_depth=16, random_state=random_state, n_jobs=-1
            )
        else:
            self.clf_pipeline = Pipeline(
                [
                    ("scaler", RobustScaler()),
                    ("clf", LogisticRegression(max_iter=1000, random_state=random_state, C=1.0)),
                ]
            )
            self.reg_pipeline = Pipeline(
                [
                    ("scaler", RobustScaler()),
                    ("reg", Ridge(alpha=1.0, random_state=random_state)),
                ]
            )
        self.classes_: Optional[np.ndarray] = None

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y_class: Union[pd.Series, np.ndarray],
        y_score: Union[pd.Series, np.ndarray],
    ) -> "MLFitPredictor":
        self.clf_pipeline.fit(X, y_class)
        self.reg_pipeline.fit(X, y_score)
        if hasattr(self.clf_pipeline, "classes_"):
            self.classes_ = self.clf_pipeline.classes_
        else:
            self.classes_ = self.clf_pipeline.named_steps["clf"].classes_
        return self

    def predict_class(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        return self.clf_pipeline.predict(X)

    def predict_score(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        raw_scores = self.reg_pipeline.predict(X)
        return np.clip(raw_scores, 0.0, 100.0)

    def predict(self, X: Union[pd.DataFrame, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        return self.predict_class(X), self.predict_score(X)

    def predict_proba(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        return self.clf_pipeline.predict_proba(X)


class FitPredictor:
    """Bộ đóng gói thống nhất (Unified Wrapper) cho Fit Prediction & Classification.

    Tự động tính toán tương tác Người <-> Áo, thực hiện cả 2 tác vụ
    Hồi quy điểm Fit và Phân loại độ vừa, đồng thời tích hợp cơ chế Fallback (TC-AI-07).
    """

    def __init__(self, model_type: str = "ml_baseline") -> None:
        self.model_type = model_type
        self.fallback_engine = RuleBasedFitPredictor()

        if model_type == "dummy":
            self.model: Any = DummyFitPredictor()
        elif model_type == "rule_based":
            self.model = self.fallback_engine
        elif model_type == "ml_baseline":
            self.model = MLFitPredictor(algorithm="linear")
        elif model_type == "random_forest":
            self.model = MLFitPredictor(algorithm="random_forest")
        else:
            raise ValueError(f"Không hỗ trợ model_type '{model_type}'")

        self.is_fitted = (model_type == "rule_based")

    def fit(
        self,
        X: Any,
        y_class: Any,
        y_score: Any,
    ) -> "FitPredictor":
        self.model.fit(X, y_class, y_score)
        self.is_fitted = True
        return self

    def predict_single(
        self,
        inputs: Dict[str, float],
    ) -> Dict[str, Any]:
        """Dự đoán độ vừa vặn cho một trường hợp Thử đồ cụ thể.

        Args:
            inputs: Dict chứa số đo người và áo (tối thiểu cần body_bust và garment_bust).

        Returns:
            Dict cấu trúc chuẩn Data Contract:
            - fit_score: Điểm số vừa vặn [0, 100].
            - classification: 'Too Tight', 'Good', hoặc 'Too Loose'.
            - confidence: Độ tin cậy dự đoán [0, 1].
            - method: Tên phương pháp suy luận.
            - fallback_used: True nếu kích hoạt fallback an toàn.
        """
        body_bust = inputs.get("body_bust")
        garment_bust = inputs.get("garment_bust")

        # Kiểm tra điều kiện Fallback khẩn cấp nếu thiếu cả 2 số đo tối thiểu
        if body_bust is None or garment_bust is None:
            return {
                "fit_score": 75.0,
                "classification": "Good",
                "confidence": 0.50,
                "method": "emergency_default",
                "fallback_used": True,
            }

        # Kiểm tra điều kiện Fallback nếu thiếu trường
        required_raw = ["body_bust", "body_height", "body_hips", "body_waist", "garment_bust", "garment_length"]
        has_all_raw = all(k in inputs for k in required_raw)

        if not self.is_fitted or not has_all_raw:
            diff = float(garment_bust) - float(body_bust)
            pred_class = get_fit_class_from_ease(diff)
            pred_score = compute_reference_fit_score(diff)
            return {
                "fit_score": round(pred_score, 1),
                "classification": pred_class,
                "confidence": 0.85,
                "method": "rule_based_fallback",
                "fallback_used": True,
            }

        # Dự đoán bằng mô hình học máy
        try:
            if self.model_type == "random_forest":
                sample = extract_fit_features_single(inputs)
                input_df = pd.DataFrame([sample])[ALL_FEATURE_COLS]
            else:
                sample = dict(inputs)
                if "bust_diff" not in sample:
                    sample["bust_diff"] = float(sample["garment_bust"]) - float(sample["body_bust"])
                input_df = pd.DataFrame([sample])[FIT_FEATURE_COLUMNS]

            pred_class = str(self.model.predict_class(input_df)[0])
            pred_score = float(self.model.predict_score(input_df)[0])

            conf = 0.90
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(input_df)[0]
                classes = list(self.model.classes_)
                conf = float(probs[classes.index(pred_class)])

            return {
                "fit_score": round(pred_score, 1),
                "classification": pred_class,
                "confidence": round(conf, 4),
                "method": self.model_type,
                "fallback_used": False,
            }
        except Exception:
            diff = float(garment_bust) - float(body_bust)
            return {
                "fit_score": round(compute_reference_fit_score(diff), 1),
                "classification": get_fit_class_from_ease(diff),
                "confidence": 0.80,
                "method": "exception_fallback",
                "fallback_used": True,
            }
