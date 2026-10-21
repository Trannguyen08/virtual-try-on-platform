"""Pydantic Schemas for AI & Fit Recommendation API (Module M4).

Cung cấp các cấu trúc dữ liệu chuẩn hóa, type-safe cho:
1. Yêu cầu & Kết quả Khuyến nghị Kích cỡ Động (Size Recommendation).
2. Yêu cầu & Kết quả Trợ lý Ảo Stylist (Fit Stylist Chatbot).
3. Đánh giá Độ vừa vặn & Báo cáo Chẩn đoán (Fit Evaluation).
4. Kiểm tra Tình trạng Hệ thống AI (AI Health Check).
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ==============================================================================
# 1. SCHEMAS CHO BỘ KHUYẾN NGHỊ KÍCH CỠ ĐỘNG (DYNAMIC SIZE ADVISOR)
# ==============================================================================
class SizeRecommendationRequest(BaseModel):
    """Payload gửi lên từ Frontend để nhận diện kích cỡ phù hợp nhất."""
    height_cm: float = Field(..., ge=120.0, le=230.0, description="Chiều cao người dùng (cm)", examples=[170.0])
    weight_kg: float = Field(..., ge=30.0, le=200.0, description="Cân nặng người dùng (kg)", examples=[65.0])
    gender: str = Field(default="male", description="Giới tính ('male', 'female', 'neutral')", examples=["male"])
    garment_category: str = Field(
        default="tshirt",
        description="Loại trang phục ('tshirt', 'shirt', 'jacket', 'pants', 'trousers')",
        examples=["tshirt"]
    )
    fit_preference: str = Field(
        default="regular",
        description="Gu mặc ('regular', 'slim', 'oversized')",
        examples=["regular"]
    )
    size_chart: Dict[str, Dict[str, float]] = Field(
        ...,
        description="Bảng size động từ shop (hỗ trợ S/M/L, 1/2/3, 38/39/40)",
        examples=[{
            "S": {"bust": 90.0, "length": 68.0, "shoulder": 41.0, "waist": 82.0},
            "M": {"bust": 98.0, "length": 70.0, "shoulder": 44.0, "waist": 90.0},
            "L": {"bust": 106.0, "length": 72.0, "shoulder": 47.0, "waist": 98.0},
            "XL": {"bust": 114.0, "length": 74.0, "shoulder": 50.0, "waist": 106.0},
        }]
    )
    body_measurements: Optional[Dict[str, float]] = Field(
        default=None,
        description="Số đo 3 vòng thực tế từ M1 (nếu có: bust, waist, hip, shoulder)",
        examples=[{"bust": 92.0, "waist": 74.0, "hip": 96.0, "shoulder": 42.0}]
    )


class RecommendationDetail(BaseModel):
    """Thông tin chi tiết về size được AI đề xuất."""
    recommended_size: str = Field(..., description="Tên size tối ưu nhất", examples=["M"])
    confidence: float = Field(..., description="Độ tin cậy theo phân phối Gauss [0.0 - 1.0]", examples=[0.88])
    actual_bust_ease_cm: float = Field(..., description="Độ cử động ngực thực tế (cm)", examples=[6.0])
    reason: str = Field(..., description="Giải thích chi tiết lý do chọn size bằng tiếng Việt")


class SizeRecommendationResponse(BaseModel):
    """Kết quả trả về cho Frontend sau khi phân tích kích cỡ."""
    status: str = Field(default="success", examples=["success"])
    recommendation: RecommendationDetail
    estimated_body_measurements: Dict[str, Any] = Field(
        ...,
        description="Số đo 4 vòng cơ thể (thực tế hoặc ước lượng từ Cao/Nặng/BMI)"
    )
    target_dimensions: Dict[str, Any] = Field(
        ...,
        description="Dải kích thước áo tối ưu theo loại vải và gu mặc"
    )
    all_candidates: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Đánh giá chi tiết của toàn bộ các size trong bảng size"
    )


# ==============================================================================
# 2. SCHEMAS CHO TRỢ LÝ ẢO STYLIST CHATBOT & GUARDRAILS
# ==============================================================================
class ChatStylistRequest(BaseModel):
    """Payload gửi tin nhắn của người dùng tới AI Stylist."""
    query: str = Field(..., min_length=1, description="Câu hỏi hoặc yêu cầu tư vấn từ khách hàng", examples=["Anh có bụng bia mặc áo thun này size M có bị lộ bụng không?"])
    height_cm: float = Field(default=170.0, ge=120.0, le=230.0, description="Chiều cao (cm)")
    weight_kg: float = Field(default=65.0, ge=30.0, le=200.0, description="Cân nặng (kg)")
    gender: str = Field(default="male", description="Giới tính")
    garment_category: str = Field(default="tshirt", description="Loại trang phục")
    fit_preference: str = Field(default="regular", description="Gu mặc")
    size_chart: Optional[Dict[str, Dict[str, float]]] = Field(default=None, description="Bảng size áo đang xem")
    body_measurements: Optional[Dict[str, float]] = Field(default=None, description="Số đo cơ thể")
    current_trial_specs: Optional[Dict[str, Any]] = Field(default=None, description="Thông số size áo đang thử trên 3D viewer")
    fit_diagnostics: Optional[Dict[str, Any]] = Field(default=None, description="Chẩn đoán độ vừa từ Mesh 3D")


class ChatStylistResponse(BaseModel):
    """Phản hồi tư vấn từ AI Stylist."""
    status: str = Field(default="success", examples=["success"])
    reply: str = Field(..., description="Câu trả lời may đo chuyên nghiệp từ AI")
    source: str = Field(..., description="Nguồn sinh câu trả lời ('gemini_llm', 'rule_based_fallback', 'domain_guardrail', 'lru_cache')")
    is_refusal: bool = Field(..., description="True nếu câu hỏi ngoài lề bị chặn bởi Guardrail")


# ==============================================================================
# 3. SCHEMAS CHO ĐÁNH GIÁ ĐỘ VỪA VẶN 3D & CHẨN ĐOÁN (FIT EVALUATION)
# ==============================================================================
class FitEvaluationRequest(BaseModel):
    """Payload yêu cầu đánh giá độ vừa giữa cơ thể và thông số trang phục."""
    body_measurements: Dict[str, float] = Field(..., description="Số đo cơ thể (ngực, eo, hông, vai)", examples=[{"bust": 92.0, "waist": 78.0, "hip": 96.0, "shoulder": 42.0}])
    garment_specs: Dict[str, float] = Field(..., description="Thông số kích thước trang phục", examples=[{"bust": 98.0, "waist": 90.0, "length": 70.0, "shoulder": 44.0}])
    garment_category: str = Field(default="tshirt", description="Loại trang phục")


class FitEvaluationResponse(BaseModel):
    """Kết quả đánh giá độ vừa vặn và phân vùng."""
    status: str = Field(default="success")
    fit_score: float = Field(..., description="Điểm vừa vặn tổng thể [0.0 - 100.0]", examples=[88.5])
    fit_class: str = Field(..., description="Phân loại ('Too Tight', 'Good', 'Too Loose')", examples=["Good"])
    region_evaluations: Dict[str, str] = Field(..., description="Đánh giá chi tiết từng vùng", examples=[{"chest": "Good", "waist": "Good", "shoulder": "Good"}])
    diagnostics: Optional[Dict[str, Any]] = Field(default=None, description="Báo cáo chẩn đoán chi tiết")


# ==============================================================================
# 4. SCHEMAS KIỂM TRA TRẠNG THÁI SẴN SÀNG (AI HEALTH CHECK)
# ==============================================================================
class AiHealthResponse(BaseModel):
    status: str = Field(default="healthy")
    module: str = Field(default="M4: Fit & AI Intelligence")
    guardrail_active: bool = Field(default=True)
    cache_capacity: int = Field(default=256)
    advisor_ready: bool = Field(default=True)
    version: str = Field(default="1.0.0")
