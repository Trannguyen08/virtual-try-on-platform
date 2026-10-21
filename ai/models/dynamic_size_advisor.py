"""Dynamic Size Advisor & Anthropometric Garment Dimension Estimator (Module M4).

Cung cấp giải pháp khuyến nghị kích cỡ thích ứng động:
1. AnthropometricEstimator: Ước lượng số đo 4 vòng chuẩn nhân trắc học từ Chiều cao (cm) & Cân nặng (kg),
   có cơ chế Fall-forward ưu tiên sử dụng 100% số đo thực tế từ 3D Mesh M1 khi có sẵn.
2. GarmentDimensionPredictor: Tính toán dải thông số trang phục lý tưởng theo phong cách mong muốn
   (Regular Fit, Slim Fit, Oversized/Relaxed).
3. DynamicSizeMatcher: Khớp kích cỡ linh hoạt với bất kỳ bảng size động nào của sản phẩm/shop
   (không cố định nhãn S/M/L, hỗ trợ cả 1/2/3, 38/39/40, v.v.).
4. DynamicSizeAdvisor: Bộ đóng gói cấp cao (Unified Orchestrator) chuẩn bị dữ liệu cho AI Chatbot & 3D Viewer.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


# ==============================================================================
# HẰNG SỐ NHÂN TRẮC HỌC, LOẠI TRANG PHỤC & ĐẶC TÍNH CO GIÃN CỦA VẢI
# ==============================================================================
FIT_PREFERENCES: List[str] = ["regular", "slim", "oversized"]
GARMENT_CATEGORIES: List[str] = ["tshirt", "shirt", "jacket", "trousers"]

# Cấu hình độ cử động chuẩn (Ease Allowance cm) phân theo Loại trang phục & Đặc tính co giãn của vải
GARMENT_CATEGORY_EASE: Dict[str, Dict[str, Dict[str, float]]] = {
    "tshirt": {
        "regular": {
            "min_ease": 4.0,
            "optimal_ease": 6.0,
            "max_ease": 9.0,
            "name_vi": "Vừa vặn chuẩn (Áo thun co giãn)",
        },
        "slim": {
            "min_ease": 0.5,
            "optimal_ease": 2.0,
            "max_ease": 3.8,
            "name_vi": "Ôm sát tôn dáng (Áo thun co giãn)",
        },
        "oversized": {
            "min_ease": 9.5,
            "optimal_ease": 14.0,
            "max_ease": 22.0,
            "name_vi": "Rộng rãi thụng (Oversized Streetwear)",
        },
    },
    "shirt": {
        "regular": {
            "min_ease": 6.5,
            "optimal_ease": 8.5,
            "max_ease": 13.0,
            "name_vi": "Vừa vặn chuẩn công sở (Sơ mi không dãn)",
        },
        "slim": {
            "min_ease": 3.5,
            "optimal_ease": 5.0,
            "max_ease": 6.4,
            "name_vi": "Slim Fit công sở (Không bị há cúc)",
        },
        "oversized": {
            "min_ease": 13.5,
            "optimal_ease": 18.0,
            "max_ease": 26.0,
            "name_vi": "Sơ mi thụng / Khoác ngoài",
        },
    },
    "jacket": {
        "regular": {
            "min_ease": 10.0,
            "optimal_ease": 14.0,
            "max_ease": 18.0,
            "name_vi": "Áo khoác vừa vặn (Mặc ngoài)",
        },
        "slim": {
            "min_ease": 7.0,
            "optimal_ease": 10.0,
            "max_ease": 13.0,
            "name_vi": "Áo khoác ôm nhẹ",
        },
        "oversized": {
            "min_ease": 18.5,
            "optimal_ease": 24.0,
            "max_ease": 32.0,
            "name_vi": "Áo khoác Oversized / Bomber",
        },
    },
}

# Tương thích ngược: Mặc định tham chiếu áo thun
EASE_TARGETS: Dict[str, Dict[str, float]] = GARMENT_CATEGORY_EASE["tshirt"]

def get_category_ease_config(garment_category: str = "tshirt", fit_preference: str = "regular") -> Dict[str, float]:
    """Lấy cấu hình độ cử động theo loại trang phục và phong cách."""
    cat = garment_category.lower()
    pref = fit_preference.lower()
    if cat not in GARMENT_CATEGORY_EASE:
        cat = "tshirt"
    if pref not in GARMENT_CATEGORY_EASE[cat]:
        pref = "regular"
    return GARMENT_CATEGORY_EASE[cat][pref]

# Bảng quy chuẩn áo thun mặc định (fallback khi shop không cung cấp size chart)
DEFAULT_GARMENT_SIZE_CHART: Dict[str, Dict[str, float]] = {
    "S": {"bust": 90.0, "length": 68.0, "shoulder": 41.0, "waist": 82.0},
    "M": {"bust": 98.0, "length": 70.0, "shoulder": 44.0, "waist": 90.0},
    "L": {"bust": 106.0, "length": 72.0, "shoulder": 47.0, "waist": 98.0},
    "XL": {"bust": 114.0, "length": 74.0, "shoulder": 50.0, "waist": 106.0},
}


# ==============================================================================
# 1. ANTHROPOMETRIC ESTIMATOR (CHIỀU CAO + CÂN NẶNG -> SỐ ĐO CƠ THỂ)
# ==============================================================================
class AnthropometricEstimator:
    """Bộ ước lượng nhân trắc học: Chuyển đổi Chiều cao và Cân nặng thành số đo cơ thể.

    Dựa trên các nghiên cứu nhân trắc học thống kê (TCVN, CAESAR, ANSUR) và chỉ số BMI.
    Hỗ trợ cơ chế Fall-forward: Nếu đã có số đo chính xác từ M1, ưu tiên sử dụng 100%.
    """

    @staticmethod
    def compute_bmi(height_cm: float, weight_kg: float) -> Tuple[float, str]:
        """Tính chỉ số BMI và phân loại thể trạng."""
        if height_cm <= 0 or weight_kg <= 0:
            return 21.5, "Bình thường"

        height_m = height_cm / 100.0
        bmi = round(weight_kg / (height_m * height_m), 1)

        if bmi < 18.5:
            category = "Gầy (Underweight)"
        elif bmi < 23.0:
            category = "Cân đối (Normal / Balanced)"
        elif bmi < 25.0:
            category = "Thừa cân nhẹ (Overweight)"
        else:
            category = "Đậm người / Béo phì (Plus-size)"

        return bmi, category

    @classmethod
    def estimate_measurements(
        cls,
        height_cm: float,
        weight_kg: float,
        gender: str = "unisex",
        body_shape: str = "balanced",
        exact_measurements: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Ước lượng chi tiết các số đo cơ thể cơ bản (cm).

        Args:
            height_cm: Chiều cao (cm).
            weight_kg: Cân nặng (kg).
            gender: Giới tính ('male', 'female', 'unisex').
            body_shape: Dáng người ('balanced', 'athletic', 'slim', 'plus_size').
            exact_measurements: Số đo thực tế đo từ 3D Mesh M1 (nếu có).

        Returns:
            Dictionary chứa các số đo: bust, waist, hip, shoulder, height, weight, bmi, category.
        """
        # Nếu đã có số đo thực tế từ 3D Mesh M1, ưu tiên sử dụng và bù trừ các trường còn thiếu
        if exact_measurements and any(k in exact_measurements for k in ["body_bust", "bust", "waist", "hip", "shoulder"]):
            h = float(height_cm)
            w = float(weight_kg)
            g = gender.lower()

            if g == "male":
                est_bust = 0.612 * w + 0.362 * h - 10.5
                est_waist = 0.785 * w + 0.125 * h - 2.0
                est_hip = 0.450 * w + 0.320 * h + 10.0
                est_shoulder = 0.115 * w + 0.185 * h + 3.0
            elif g == "female":
                est_bust = 0.585 * w + 0.315 * h - 5.0
                est_waist = 0.620 * w + 0.160 * h - 8.0
                est_hip = 0.680 * w + 0.280 * h + 5.0
                est_shoulder = 0.085 * w + 0.170 * h + 5.0
            else:  # unisex
                est_bust = 0.598 * w + 0.338 * h - 7.5
                est_waist = 0.702 * w + 0.142 * h - 5.0
                est_hip = 0.565 * w + 0.300 * h + 7.5
                est_shoulder = 0.100 * w + 0.178 * h + 4.0

            b_bust = exact_measurements.get("body_bust") or exact_measurements.get("bust") or est_bust
            b_waist = exact_measurements.get("body_waist") or exact_measurements.get("waist") or est_waist
            b_hip = exact_measurements.get("body_hip") or exact_measurements.get("hip") or est_hip
            b_shoulder = exact_measurements.get("body_shoulder") or exact_measurements.get("shoulder") or est_shoulder

            bmi, category = cls.compute_bmi(height_cm, weight_kg)
            return {
                "bust": round(float(b_bust), 1),
                "waist": round(float(b_waist), 1),
                "hip": round(float(b_hip), 1),
                "shoulder": round(float(b_shoulder), 1),
                "height": round(float(height_cm), 1),
                "weight": round(float(weight_kg), 1),
                "bmi": bmi,
                "body_category": category,
                "source": "exact_3d_mesh",
            }

        # Nếu chưa có số đo 3D, tiến hành ước lượng từ Chiều cao và Cân nặng
        h = float(height_cm)
        w = float(weight_kg)
        g = gender.lower()

        if g == "male":
            est_bust = 0.612 * w + 0.362 * h - 10.5
            est_waist = 0.785 * w + 0.125 * h - 2.0
            est_hip = 0.450 * w + 0.320 * h + 10.0
            est_shoulder = 0.115 * w + 0.185 * h + 3.0
        elif g == "female":
            est_bust = 0.585 * w + 0.315 * h - 5.0
            est_waist = 0.620 * w + 0.160 * h - 8.0
            est_hip = 0.680 * w + 0.280 * h + 5.0
            est_shoulder = 0.085 * w + 0.170 * h + 5.0
        else:  # unisex
            est_bust = 0.598 * w + 0.338 * h - 7.5
            est_waist = 0.702 * w + 0.142 * h - 5.0
            est_hip = 0.565 * w + 0.300 * h + 7.5
            est_shoulder = 0.100 * w + 0.178 * h + 4.0

        # Điều chỉnh theo dáng người (Body Shape Modifier)
        shape = body_shape.lower()
        if shape == "athletic":  # Vận động viên / gymer: Vai và ngực nở, eo thon
            est_bust += 3.0
            est_shoulder += 2.0
            est_waist -= 3.0
        elif shape == "slim":  # Mảnh khảnh
            est_bust -= 2.0
            est_waist -= 2.0
        elif shape in ["plus_size", "apple"]:  # Vòng bụng to
            est_waist += 4.5
            est_bust += 1.5

        bmi, category = cls.compute_bmi(h, w)

        return {
            "bust": round(float(est_bust), 1),
            "waist": round(float(est_waist), 1),
            "hip": round(float(est_hip), 1),
            "shoulder": round(float(est_shoulder), 1),
            "height": round(h, 1),
            "weight": round(w, 1),
            "bmi": bmi,
            "body_category": category,
            "source": "anthropometric_estimation",
        }


# ==============================================================================
# 2. GARMENT DIMENSION PREDICTOR (SỐ ĐO BODY -> DẢI THÔNG SỐ ÁO LÝ TƯỞNG)
# ==============================================================================
class GarmentDimensionPredictor:
    """Bộ dự đoán dải thông số áo tối ưu dựa trên số đo cơ thể và phong cách mong muốn."""

    @classmethod
    def predict_target_range(
        cls,
        body_measurements: Dict[str, float],
        fit_preference: str = "regular",
        garment_category: str = "tshirt",
    ) -> Dict[str, Any]:
        """Tính dải thông số áo lý tưởng (Target Specs Range) theo loại trang phục và form dáng.

        Args:
            body_measurements: Dict chứa số đo bust, waist, shoulder, height.
            fit_preference: 'regular', 'slim', hoặc 'oversized'.
            garment_category: 'tshirt', 'shirt', 'jacket', hoặc 'trousers'.

        Returns:
            Dict chứa khoảng kích thước đề xuất (min, optimal, max) cho từng thông số áo.
        """
        targets = get_category_ease_config(garment_category=garment_category, fit_preference=fit_preference)
        pref = fit_preference.lower()

        b_bust = body_measurements.get("bust", 92.0)
        b_waist = body_measurements.get("waist", 74.0)
        b_shoulder = body_measurements.get("shoulder", 42.0)
        b_height = body_measurements.get("height", 170.0)

        min_bust = round(b_bust + targets["min_ease"], 1)
        opt_bust = round(b_bust + targets["optimal_ease"], 1)
        max_bust = round(b_bust + targets["max_ease"], 1)

        # Chiều dài áo tiêu chuẩn (tỷ lệ 40 - 43% chiều cao, áo khoác/sơ mi dài hơn 1-2cm)
        length_offset = 2.0 if garment_category.lower() in ["shirt", "jacket"] else 0.0
        opt_length = round(b_height * 0.412 + length_offset, 1)
        min_length = round(opt_length - 2.5, 1)
        max_length = round(opt_length + 3.0, 1)

        # Rộng vai áo
        if pref == "oversized":
            min_sh = round(b_shoulder + 3.0, 1)
            opt_sh = round(b_shoulder + 5.5, 1)
            max_sh = round(b_shoulder + 8.5, 1)
        elif pref == "slim":
            min_sh = round(b_shoulder - 0.5, 1)
            opt_sh = round(b_shoulder + 1.0, 1)
            max_sh = round(b_shoulder + 2.0, 1)
        else:  # regular
            min_sh = round(b_shoulder + 1.0, 1)
            opt_sh = round(b_shoulder + 2.0, 1)
            max_sh = round(b_shoulder + 3.5, 1)

        return {
            "fit_preference": pref,
            "garment_category": garment_category,
            "style_name_vi": targets["name_vi"],
            "target_bust_range_cm": {
                "min": min_bust,
                "optimal": opt_bust,
                "max": max_bust,
            },
            "target_length_range_cm": {
                "min": min_length,
                "optimal": opt_length,
                "max": max_length,
            },
            "target_shoulder_range_cm": {
                "min": min_sh,
                "optimal": opt_sh,
                "max": max_sh,
            },
            "recommended_ease_cm": targets["optimal_ease"],
        }


# ==============================================================================
# 3. DYNAMIC SIZE MATCHER (KHỚP SIZE VỚI BẢNG SIZE BẤT KỲ CỦA SHOP)
# ==============================================================================
class DynamicSizeMatcher:
    """Bộ khớp kích cỡ động: Đối chiếu số đo cơ thể với bảng size của bất kỳ sản phẩm nào.

    Hoạt động độc lập với tên nhãn (S, M, L, XL hoặc 1, 2, 3 hoặc 38, 39, 40).
    """

    @classmethod
    def match_size_chart(
        cls,
        body_measurements: Dict[str, float],
        size_chart: Dict[str, Dict[str, float]],
        fit_preference: str = "regular",
        garment_category: str = "tshirt",
    ) -> Dict[str, Any]:
        """Khớp kích cỡ tối ưu từ bảng size được cung cấp.

        Args:
            body_measurements: Số đo cơ thể thực tế hoặc ước lượng (cm).
            size_chart: Bảng thông số kỹ thuật của sản phẩm.
            fit_preference: Phong cách ('regular', 'slim', 'oversized').
            garment_category: Loại đồ ('tshirt', 'shirt', 'jacket', 'trousers').

        Returns:
            Dict chứa size đề xuất, độ tin cậy, phân tích từng size và giải thích cụ thể.
        """
        target_cfg = get_category_ease_config(garment_category=garment_category, fit_preference=fit_preference)
        target_optimal_ease = target_cfg["optimal_ease"]
        pref = fit_preference.lower()
        cat = garment_category.lower()

        # Ngưỡng tối thiểu để áo có thể cử động được mà không bị chật bó
        min_wearable_ease = 3.5 if cat == "shirt" else (7.0 if cat == "jacket" else 1.0)

        b_bust = body_measurements.get("bust", 92.0)
        b_waist = body_measurements.get("waist", 74.0)
        b_shoulder = body_measurements.get("shoulder", 42.0)

        size_analysis: List[Dict[str, Any]] = []
        best_size: Optional[str] = None
        min_deviation = float("inf")

        for size_key, specs in size_chart.items():
            g_bust = float(specs.get("bust", 0.0))
            g_length = float(specs.get("length", 0.0))
            g_shoulder = float(specs.get("shoulder", 0.0))
            g_waist = float(specs.get("waist", 0.0))

            ease = g_bust - b_bust
            deviation = abs(ease - target_optimal_ease)

            # Phân loại phong cách mặc thực tế của size này đối với người dùng
            if ease < min_wearable_ease:
                fit_category = "Too Tight (Quá chật / Bó căng)"
                is_wearable = False
            elif ease < target_cfg["min_ease"]:
                fit_category = "Slim Fit (Ôm vừa)"
                is_wearable = True
            elif ease <= target_cfg["max_ease"]:
                fit_category = f"Standard {pref.capitalize()} (Vừa vặn chuẩn)"
                is_wearable = True
            else:
                fit_category = "Oversized (Rộng rãi / Thoải mái)"
                is_wearable = True

            # Chỉ cân nhắc đề xuất size nếu không bị chật
            if is_wearable:
                if deviation < min_deviation:
                    min_deviation = deviation
                    best_size = size_key

            size_analysis.append({
                "size": size_key,
                "garment_bust_cm": g_bust,
                "garment_length_cm": g_length,
                "garment_shoulder_cm": g_shoulder,
                "garment_waist_cm": g_waist,
                "bust_ease_cm": round(ease, 1),
                "shoulder_diff_cm": round(g_shoulder - b_shoulder, 1) if g_shoulder > 0 else 0.0,
                "fit_category": fit_category,
                "is_wearable": is_wearable,
                "deviation_from_optimal_cm": round(deviation, 1),
            })

        # Nếu tất cả size đều chật (ví dụ người to nhưng áo toàn size nhỏ), chọn size lớn nhất
        if best_size is None:
            best_size = list(size_chart.keys())[-1]

        best_specs = size_chart[best_size]
        best_bust = float(best_specs.get("bust", 0.0))
        best_ease = round(best_bust - b_bust, 1)

        # Tính độ tin cậy chuẩn hóa theo khoảng cách Gauss: e^(-dev / 10)
        confidence = float(np.clip(np.exp(-min_deviation / 8.0), 0.50, 0.98))

        # Đánh dấu is_recommended trong danh sách
        for item in size_analysis:
            item["is_recommended"] = (item["size"] == best_size)

        # Soạn lời giải thích rõ ràng, thân thiện cho người dùng
        reason = (
            f"Đề xuất {best_size} vì áo có vòng ngực {best_bust:.1f} cm, mang lại độ cử động {best_ease:+.1f} cm "
            f"so với vòng ngực {b_bust:.1f} cm của bạn, đạt tiêu chuẩn {target_cfg['name_vi']} "
            f"(chuẩn lý tưởng: +{target_optimal_ease:.1f} cm)."
        )

        return {
            "recommended_size": best_size,
            "confidence": round(confidence, 2),
            "fit_preference": pref,
            "garment_category": cat,
            "garment_specs_cm": best_specs,
            "actual_bust_ease_cm": best_ease,
            "reason": reason,
            "all_sizes_analysis": size_analysis,
        }


# ==============================================================================
# 4. UNIFIED DYNAMIC SIZE ADVISOR (BỘ ĐIỀU PHỐI ĐA TẦNG CHO M4)
# ==============================================================================
class DynamicSizeAdvisor:
    """Bộ điều phối tư vấn kích cỡ thích ứng động toàn diện cho Module M4.

    Hỗ trợ mọi trường hợp đầu vào:
    - Người dùng chỉ có Chiều cao & Cân nặng -> Tự động ước lượng nhân trắc học.
    - Người dùng đã có số đo 3D chính xác từ M1 -> Ưu tiên dùng số đo chuẩn.
    - Cung cấp bất kỳ bảng size nào từ shop -> Tự động khớp và đưa ra khuyến nghị.
    """

    def __init__(self) -> None:
        self.estimator = AnthropometricEstimator()
        self.dimension_predictor = GarmentDimensionPredictor()
        self.matcher = DynamicSizeMatcher()

    def advise(
        self,
        height_cm: float = 170.0,
        weight_kg: float = 65.0,
        gender: str = "unisex",
        body_shape: str = "balanced",
        body_measurements: Optional[Dict[str, float]] = None,
        size_chart: Optional[Dict[str, Dict[str, float]]] = None,
        fit_preference: str = "regular",
        garment_category: str = "tshirt",
    ) -> Dict[str, Any]:
        """Tư vấn kích cỡ trang phục toàn diện.

        Args:
            height_cm: Chiều cao (cm).
            weight_kg: Cân nặng (kg).
            gender: 'male', 'female', hoặc 'unisex'.
            body_shape: 'balanced', 'athletic', 'slim', 'plus_size'.
            body_measurements: Số đo thực tế từ M1 (nếu có).
            size_chart: Bảng thông số đo của sản phẩm (nếu None, dùng bảng chuẩn).
            fit_preference: 'regular', 'slim', 'oversized'.
            garment_category: 'tshirt', 'shirt', 'jacket', 'trousers'.

        Returns:
            Dictionary tư vấn kích cỡ chi tiết, bao gồm cả số đo cơ thể, dải thông số lý tưởng,
            size đề xuất và phân tích toàn bộ bảng size.
        """
        # Bước 1: Ước lượng hoặc tiếp nhận số đo cơ thể
        body = self.estimator.estimate_measurements(
            height_cm=height_cm,
            weight_kg=weight_kg,
            gender=gender,
            body_shape=body_shape,
            exact_measurements=body_measurements,
        )

        # Bước 2: Dự đoán dải kích thước áo lý tưởng
        target_range = self.dimension_predictor.predict_target_range(
            body_measurements=body,
            fit_preference=fit_preference,
            garment_category=garment_category,
        )

        # Bước 3: Khớp size với bảng size động
        chart = size_chart or DEFAULT_GARMENT_SIZE_CHART
        matching_result = self.matcher.match_size_chart(
            body_measurements=body,
            size_chart=chart,
            fit_preference=fit_preference,
            garment_category=garment_category,
        )

        return {
            "status": "success",
            "body_profile": body,
            "target_garment_dimension_range": target_range,
            "recommendation": matching_result,
        }
