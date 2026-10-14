"""Size Recommender Baseline Models for Module M4.

Provides 3 baseline levels:
1. DummySizeRecommender (Floor threshold / Majority Class)
2. RuleBasedSizeRecommender (Heuristic / Geometry Fallback System - TC-AI-07)
3. MLSizeRecommender (Logistic Regression / Random Forest with Robust Scaling)
And a unified SizeRecommender wrapper with automatic fallback capability.
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

from ai.dataset.labeling.size_labeler import SIZE_ORDER, get_size_from_bust

FEATURE_COLUMNS: List[str] = [
    "body_bust",
    "body_height",
    "body_hips",
    "body_waist",
]


class RuleBasedSizeRecommender:
    """Baseline 2: Hệ thống phân loại dựa trên luật hình học (Rule-based Heuristic).

    Đóng vai trò là hệ thống dự phòng (Fallback System - TC-AI-07) khi AI lỗi hoặc thiếu trường.
    """

    def __init__(self) -> None:
        self.classes_ = np.array(SIZE_ORDER)

    def fit(self, X: Any = None, y: Any = None) -> "RuleBasedSizeRecommender":
        """Không cần huấn luyện, tuân thủ interface của scikit-learn."""
        return self

    def predict(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """Dự đoán kích cỡ từ mảng/DataFrame đầu vào."""
        if isinstance(X, pd.DataFrame):
            if "body_bust" in X.columns:
                busts = X["body_bust"].values
            else:
                busts = X.iloc[:, 0].values
        else:
            # Giả định cột 0 là body_bust nếu là numpy array
            busts = X[:, 0]

        preds = [get_size_from_bust(float(b)) for b in busts]
        return np.array(preds)

    def predict_proba(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """Trả về xác suất 1.0 cho nhãn được phân loại theo luật."""
        preds = self.predict(X)
        probs = np.zeros((len(preds), len(self.classes_)))
        for i, pred in enumerate(preds):
            idx = list(self.classes_).index(pred)
            probs[i, idx] = 1.0
        return probs


class DummySizeRecommender:
    """Baseline 1: Mô hình cơ sở ngẫu nhiên / lớp đa số (Ngưỡng sàn tối thiểu)."""

    def __init__(self, strategy: str = "most_frequent") -> None:
        self.model = DummyClassifier(strategy=strategy, random_state=42)
        self.classes_: Optional[np.ndarray] = None

    def fit(self, X: Any, y: Any) -> "DummySizeRecommender":
        self.model.fit(X, y)
        self.classes_ = self.model.classes_
        return self

    def predict(self, X: Any) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: Any) -> np.ndarray:
        return self.model.predict_proba(X)


class MLSizeRecommender:
    """Baseline 3: Mô hình học máy cơ sở (Logistic Regression đa lớp)."""

    def __init__(
        self,
        model_type: str = "logistic_regression",
        random_state: int = 42,
    ) -> None:
        self.model_type = model_type
        self.random_state = random_state

        if model_type == "logistic_regression":
            classifier = LogisticRegression(
                max_iter=1000,
                random_state=random_state,
                C=1.0,
            )
        else:
            raise ValueError(f"Kiểu mô hình không được hỗ trợ: {model_type}")

        # Kết hợp RobustScaler do dữ liệu có outliers (được phát hiện ở EDA)
        self.pipeline = Pipeline(
            [
                ("scaler", RobustScaler()),
                ("clf", classifier),
            ]
        )
        self.classes_: Optional[np.ndarray] = None

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray],
    ) -> "MLSizeRecommender":
        self.pipeline.fit(X, y)
        self.classes_ = self.pipeline.named_steps["clf"].classes_
        return self

    def predict(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        return self.pipeline.predict(X)

    def predict_proba(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        return self.pipeline.predict_proba(X)


class SizeRecommender:
    """Bộ đóng gói thống nhất (Unified Wrapper) cho hệ thống Size Recommendation.

    Hỗ trợ chuyển đổi linh hoạt giữa các mô hình và tự động kích hoạt
    cơ chế Fallback (TC-AI-07) khi gặp dữ liệu dị thường hoặc thiếu đặc trưng.
    """

    def __init__(self, model_type: str = "logistic_regression") -> None:
        self.model_type = model_type
        self.fallback_engine = RuleBasedSizeRecommender()

        if model_type == "dummy":
            self.model: Any = DummySizeRecommender()
        elif model_type == "rule_based":
            self.model = self.fallback_engine
        elif model_type == "logistic_regression":
            self.model = MLSizeRecommender(model_type="logistic_regression")
        else:
            raise ValueError(f"Không hỗ trợ model_type '{model_type}'")

        self.is_fitted = (model_type == "rule_based")

    def fit(self, X: Any, y: Any) -> "SizeRecommender":
        self.model.fit(X, y)
        self.is_fitted = True
        return self

    def predict(self, X: Any) -> np.ndarray:
        if not self.is_fitted:
            # Tự động fallback nếu model ML chưa fit
            return self.fallback_engine.predict(X)
        return self.model.predict(X)

    def predict_proba(self, X: Any) -> np.ndarray:
        if not self.is_fitted:
            return self.fallback_engine.predict_proba(X)
        return self.model.predict_proba(X)

    def recommend_single(
        self,
        measurements: Dict[str, float],
    ) -> Dict[str, Any]:
        """Đề xuất size cho một cá nhân từ dictionary số đo.

        Tự động fallback an toàn (Zero Crash) nếu thiếu trường hoặc lỗi.

        Args:
            measurements: Dict chứa 'body_bust', 'body_height', 'body_hips', 'body_waist'.

        Returns:
            Dict chứa 'recommended_size', 'confidence', 'method', 'fallback_used'.
        """
        # Kiểm tra điều kiện fallback
        has_all_features = all(k in measurements for k in FEATURE_COLUMNS)

        if not self.is_fitted or not has_all_features:
            # Kích hoạt Fallback
            bust_val = measurements.get("body_bust")
            if bust_val is None or not np.isfinite(bust_val):
                return {
                    "recommended_size": "M",  # Default fallback an toàn
                    "confidence": 0.50,
                    "method": "emergency_default",
                    "fallback_used": True,
                }

            fallback_size = get_size_from_bust(float(bust_val))
            return {
                "recommended_size": fallback_size,
                "confidence": 0.85,
                "method": "rule_based_fallback",
                "fallback_used": True,
            }

        try:
            input_df = pd.DataFrame([measurements])[FEATURE_COLUMNS]
            pred_size = str(self.model.predict(input_df)[0])
            probs = self.model.predict_proba(input_df)[0]
            classes = list(self.model.classes_)
            conf = float(probs[classes.index(pred_size)])

            return {
                "recommended_size": pred_size,
                "confidence": round(conf, 4),
                "method": self.model_type,
                "fallback_used": False,
            }
        except Exception:
            # Fallback nếu model ML có ngoại lệ
            bust_val = float(measurements.get("body_bust", 100.0))
            return {
                "recommended_size": get_size_from_bust(bust_val),
                "confidence": 0.80,
                "method": "exception_fallback",
                "fallback_used": True,
            }
