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
        size_chart: Optional[Dict[str, Dict[str, float]]] = None,
        garment_specs: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Đề xuất size tối ưu cho một cá nhân dựa trên số đo cơ thể và thông số thực tế của trang phục.

        Nếu có size_chart hoặc garment_specs, hệ thống sẽ đối chiếu số đo người dùng với bảng
        thông số kỹ thuật của trang phục để tính toán độ cử động (Ease Allowance) chuẩn xác.
        Nếu không có thông số trang phục, tự động sử dụng mô hình ML hoặc luật dự phòng (Zero Crash).

        Args:
            measurements: Dict chứa số đo cơ thể ('body_bust', 'body_height', 'body_hips', 'body_waist').
            size_chart: Bảng thông số kỹ thuật từng size của trang phục (cm).
            garment_specs: Thông số chiếc áo cụ thể đang thử (nếu có).

        Returns:
            Dict chứa 'recommended_size', 'confidence', 'method', 'fallback_used', 'garment_specs'.
        """
        body_bust = measurements.get("body_bust", measurements.get("bust"))

        # Nếu có thông số trang phục (size_chart hoặc garment_specs), ưu tiên đối chiếu thông số thực tế
        if (size_chart is not None or garment_specs is not None) and body_bust is not None and np.isfinite(body_bust):
            chart = size_chart or {
                "S": {"bust": 90.0, "length": 68.0, "shoulder": 41.0, "waist": 82.0},
                "M": {"bust": 98.0, "length": 70.0, "shoulder": 44.0, "waist": 90.0},
                "L": {"bust": 106.0, "length": 72.0, "shoulder": 47.0, "waist": 98.0},
                "XL": {"bust": 114.0, "length": 74.0, "shoulder": 50.0, "waist": 106.0},
            }
            best_size = "M"
            min_dist_to_optimal = float("inf")
            for s_name in SIZE_ORDER:
                s_bust = chart.get(s_name, {}).get("bust", 0.0)
                s_ease = s_bust - float(body_bust)
                if s_ease >= 2.0:
                    dist = abs(s_ease - 6.0)
                    if dist < min_dist_to_optimal:
                        min_dist_to_optimal = dist
                        best_size = s_name

            rec_specs = chart.get(best_size, chart.get("M", {}))
            rec_bust = rec_specs.get("bust", 98.0)
            rec_ease = rec_bust - float(body_bust)

            return {
                "recommended_size": best_size,
                "confidence": 0.96,
                "method": "garment_specs_fit_matching",
                "fallback_used": False,
                "garment_specs": rec_specs,
                "ease_cm": round(rec_ease, 1),
                "reason": (
                    f"Đề xuất Size {best_size} vì áo có vòng ngực {rec_bust:.1f} cm mang lại độ cử động {rec_ease:+.1f} cm "
                    f"so với vòng ngực {float(body_bust):.1f} cm (chuẩn vừa vặn Regular Fit 4-8 cm)."
                ),
            }

        # Kiểm tra điều kiện fallback khi không có bảng thông số trang phục
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
