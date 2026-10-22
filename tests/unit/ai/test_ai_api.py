"""Unit Test Suite cho FastAPI Router của Module M4: AI & Fit Services.

Kiểm thử:
1. GET /api/v1/ai/health: Trả về trạng thái healthy.
2. POST /api/v1/ai/recommend-size: Nhận diện size chuẩn (S/M/L/XL) và size Local Brand (1/2/3).
3. POST /api/v1/ai/chat: Phản hồi tư vấn và câu hỏi chung qua Gemini.
4. POST /api/v1/ai/evaluate-fit: Tính điểm Fit Score giải tích và phân lớp từng vùng.
5. Validation Error: Bắt lỗi 422 khi input không hợp lệ.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from ai.api.router import _chatbot

client = TestClient(app)


# ==============================================================================
# 1. TEST HEALTH CHECK
# ==============================================================================
@pytest.mark.fast
def test_ai_health_endpoint():
    """Kiểm tra endpoint health check của AI Router."""
    response = client.get("/api/v1/ai/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "M4" in data["module"]
    assert data["guardrail_active"] is False
    assert data["advisor_ready"] is True


# ==============================================================================
# 2. TEST DYNAMIC SIZE RECOMMENDATION
# ==============================================================================
@pytest.mark.fast
def test_recommend_size_endpoint_standard():
    """Kiểm tra API gợi ý size cho áo thun với bảng size S/M/L/XL chuẩn."""
    payload = {
        "height_cm": 170.0,
        "weight_kg": 65.0,
        "gender": "male",
        "garment_category": "tshirt",
        "fit_preference": "regular",
        "size_chart": {
            "S": {"bust": 90.0, "length": 68.0, "shoulder": 41.0},
            "M": {"bust": 98.0, "length": 70.0, "shoulder": 44.0},
            "L": {"bust": 106.0, "length": 72.0, "shoulder": 47.0},
        },
    }
    response = client.post("/api/v1/ai/recommend-size", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["recommendation"]["recommended_size"] == "M"
    assert data["recommendation"]["confidence"] >= 0.70
    assert "estimated_body_measurements" in data
    assert "all_candidates" in data


@pytest.mark.fast
def test_recommend_size_endpoint_local_brand():
    """Kiểm tra API khớp size trên bảng size lạ (Size 1, 2, 3) phong cách oversized."""
    payload = {
        "height_cm": 170.0,
        "weight_kg": 65.0,
        "garment_category": "tshirt",
        "fit_preference": "oversized",
        "size_chart": {
            "Size 1": {"bust": 94.0, "length": 69.0, "shoulder": 43.0},
            "Size 2": {"bust": 100.0, "length": 72.0, "shoulder": 46.0},
            "Size 3": {"bust": 108.0, "length": 75.0, "shoulder": 49.0},
        },
    }
    response = client.post("/api/v1/ai/recommend-size", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["recommendation"]["recommended_size"] in ["Size 2", "Size 3"]


# ==============================================================================
# 3. TEST AI STYLIST CHAT & GUARDRAILS
# ==============================================================================
@pytest.mark.fast
def test_chat_endpoint_valid_fashion_query(monkeypatch):
    """Kiểm tra API Chatbot trả lời câu hỏi thời trang hợp lệ."""
    monkeypatch.setattr(_chatbot, "api_key", "test-key")
    monkeypatch.setattr(_chatbot, "_call_gemini_rest_api", lambda prompt: "Áo size M có thể phù hợp; hãy đối chiếu bảng size thực tế.")
    payload = {
        "query": "Anh cao 1m70 nặng 65kg, mặc áo thun này lấy size nào vừa đẹp?",
        "height_cm": 170.0,
        "weight_kg": 65.0,
        "size_chart": {
            "S": {"bust": 90.0, "length": 68.0},
            "M": {"bust": 98.0, "length": 70.0},
            "L": {"bust": 106.0, "length": 72.0},
        },
    }
    response = client.post("/api/v1/ai/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["is_refusal"] is False
    assert len(data["reply"]) > 20


@pytest.mark.fast
def test_chat_endpoint_answers_off_topic_query(monkeypatch):
    """TC-AI-CHAT-03: API chuyển câu hỏi ngoài thời trang đến Gemini."""
    monkeypatch.setattr(_chatbot, "api_key", "test-key")
    monkeypatch.setattr(_chatbot, "_call_gemini_rest_api", lambda prompt: "Tôi chưa có dữ liệu thời tiết trực tiếp.")
    payload = {
        "query": "Dự báo thời tiết ngày mai ở Đà Nẵng thế nào có mưa không?",
    }
    response = client.post("/api/v1/ai/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["is_refusal"] is False
    assert data["source"] == "gemini_llm"
    assert "thời tiết" in data["reply"]


# ==============================================================================
# 4. TEST FIT EVALUATION
# ==============================================================================
@pytest.mark.fast
def test_evaluate_fit_endpoint():
    """Kiểm tra API đánh giá độ vừa vặn giữa cơ thể và thông số áo."""
    payload = {
        "body_measurements": {"bust": 92.0, "waist": 78.0, "shoulder": 42.0},
        "garment_specs": {"bust": 98.0, "waist": 88.0, "shoulder": 44.0, "length": 70.0},
        "garment_category": "tshirt",
    }
    response = client.post("/api/v1/ai/evaluate-fit", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert 0.0 <= data["fit_score"] <= 100.0
    assert data["fit_class"] in ["Good", "Too Tight", "Too Loose"]
    assert "chest" in data["region_evaluations"]


# ==============================================================================
# 5. TEST INPUT VALIDATION (422)
# ==============================================================================
@pytest.mark.fast
def test_validation_error_on_invalid_height():
    """Kiểm tra bắt lỗi 422 khi chiều cao ngoài ngưỡng hợp lệ."""
    payload = {
        "height_cm": 50.0,  # Dưới min 120cm
        "weight_kg": 65.0,
        "size_chart": {"M": {"bust": 98.0}},
    }
    response = client.post("/api/v1/ai/recommend-size", json=payload)
    assert response.status_code == 422
