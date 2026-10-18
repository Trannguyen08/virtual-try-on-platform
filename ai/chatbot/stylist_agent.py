"""AI Fit Stylist Chatbot Agent for Virtual Try-On Platform (Module M4).

Cung cấp:
1. FitStylistChatbot: Tác nhân tư vấn kích cỡ & form dáng hội thoại thời gian thực.
2. Tích hợp đa tầng:
   - Tầng Guardrails: Chặn 100% câu hỏi ngoài lề (lập trình, thời tiết, chính trị) mà không tốn API.
   - Tầng Cache & Concurrency: Cache phản hồi tương tự, chịu tải cao khi nhiều người truy cập cùng lúc.
   - Tầng LLM: Kết nối Google Gemini API (gemini-1.5-flash) bất đồng bộ.
   - Tầng Zero-Crash Fallback: Tự động chuyển sang Rule-based Stylist khi không có API Key hoặc mất mạng.
"""

import asyncio
import hashlib
import json
import os
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.request

from ai.chatbot.guardrails import ConcurrencyGovernor, DomainGuardrail, LRUResponseCache
from ai.chatbot.prompt_templates import (
    SYSTEM_INSTRUCTION_STYLIST,
    build_stylist_context_prompt,
)
from ai.models.dynamic_size_advisor import DynamicSizeAdvisor


class FitStylistChatbot:
    """Tác nhân AI tư vấn thời trang ảo (Virtual Try-On AI Stylist)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-1.5-flash",
        max_concurrent: int = 10,
        cache_capacity: int = 256,
    ) -> None:
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.model_name = model_name
        self.guardrail = DomainGuardrail()
        self.cache = LRUResponseCache(capacity=cache_capacity)
        self.governor = ConcurrencyGovernor(max_concurrent_requests=max_concurrent)
        self.advisor = DynamicSizeAdvisor()

    def _make_context_hash(self, user_profile: Dict[str, Any], size_chart: Optional[Dict[str, Any]], garment_category: str) -> str:
        """Tạo chuỗi băm đại diện cho ngữ cảnh đo đạc."""
        summary = f"{user_profile.get('height')}_{user_profile.get('weight')}_{user_profile.get('bust')}_{garment_category}"
        if size_chart:
            summary += f"_{len(size_chart)}"
        return hashlib.md5(summary.encode("utf-8")).hexdigest()

    def _generate_rule_based_advice(
        self,
        user_query: str,
        user_profile: Dict[str, Any],
        size_chart: Optional[Dict[str, Dict[str, float]]] = None,
        fit_diagnostics: Optional[Dict[str, Any]] = None,
        garment_category: str = "tshirt",
        fit_preference: str = "regular",
    ) -> str:
        """Bộ sinh lời khuyên may đo giải tích (Zero-Crash Fallback) khi không dùng LLM API."""
        adv_res = self.advisor.advise(
            height_cm=float(user_profile.get("height", 170.0)),
            weight_kg=float(user_profile.get("weight", 65.0)),
            gender=user_profile.get("gender", "unisex"),
            body_shape=user_profile.get("body_shape", "balanced"),
            body_measurements=user_profile,
            size_chart=size_chart,
            fit_preference=fit_preference,
            garment_category=garment_category,
        )

        rec = adv_res["recommendation"]
        rec_size = rec["recommended_size"]
        specs = rec["garment_specs_cm"]
        ease = rec["actual_bust_ease_cm"]
        b_bust = user_profile.get("bust", 92.0)

        cat_name = "áo sơ mi" if garment_category == "shirt" else ("áo khoác" if garment_category == "jacket" else "áo thun")

        response_parts = []
        response_parts.append(
            f"Dạ dựa trên số đo của anh/chị (ngực {b_bust:.1f} cm, chiều cao {user_profile.get('height', 170.0)} cm, "
            f"cân nặng {user_profile.get('weight', 65.0)} kg), em xin tư vấn kích cỡ tối ưu cho chiếc {cat_name} này:"
        )

        response_parts.append(
            f"- **Kích cỡ khuyên dùng:** **{rec_size}** (Vòng ngực áo {specs.get('bust', 0.0):.1f} cm, "
            f"dài áo {specs.get('length', 0.0):.1f} cm, vai {specs.get('shoulder', 0.0):.1f} cm)."
        )

        if garment_category == "shirt":
            response_parts.append(
                f"- **Đánh giá form dáng:** Áo sơ mi là chất vải dệt thoi không co giãn. Size {rec_size} "
                f"cho độ cử động {ease:+.1f} cm là mức lý tưởng để khi cài cúc ngực không bị căng há cúc và cử động giơ tay thoải mái."
            )
        else:
            response_parts.append(
                f"- **Đánh giá form dáng:** Áo có độ cử động {ease:+.1f} cm, ôm vừa vặn tự nhiên chuẩn {adv_res['target_garment_dimension_range']['style_name_vi']}."
            )

        # Kiểm tra nếu khách hỏi về giấu bụng hoặc mặc rộng
        q_lower = user_query.lower()
        if any(w in q_lower for w in ["bụng", "rộng", "thụng", "oversize", "thoải mái"]):
            response_parts.append(
                "- **Lời khuyên gu mặc:** Nếu anh/chị thích mặc form rộng thoải mái hoặc muốn giấu bụng tốt hơn, "
                "anh/chị hoàn toàn có thể tăng lên 1 size so với kích cỡ đề xuất trên mà vai áo vẫn không bị xệ quá nhiều ạ!"
            )

        response_parts.append("Anh/chị có muốn em kiểm tra thêm vùng nào trên mô hình 3D không ạ?")
        return "\n".join(response_parts)

    def _call_gemini_rest_api(self, prompt: str) -> str:
        """Gọi Google Gemini REST API thông qua thư viện chuẩn urllib (Không phụ thuộc pip bên ngoài)."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY chưa được thiết lập.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": SYSTEM_INSTRUCTION_STYLIST}]
            },
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 500,
            },
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=10.0) as response:
            result_data = json.loads(response.read().decode("utf-8"))
            candidates = result_data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return str(parts[0].get("text", "")).strip()

        raise RuntimeError("Không nhận được phản hồi hợp lệ từ Gemini API.")

    async def ask_async(
        self,
        user_query: str,
        height_cm: float = 170.0,
        weight_kg: float = 65.0,
        body_measurements: Optional[Dict[str, float]] = None,
        size_chart: Optional[Dict[str, Dict[str, float]]] = None,
        current_trial_specs: Optional[Dict[str, Any]] = None,
        fit_diagnostics: Optional[Dict[str, Any]] = None,
        garment_category: str = "tshirt",
        fit_preference: str = "regular",
    ) -> Dict[str, Any]:
        """Tư vấn kích cỡ và form dáng bất đồng bộ (Non-blocking Async).

        Args:
            user_query: Câu hỏi của người dùng.
            height_cm: Chiều cao (cm).
            weight_kg: Cân nặng (kg).
            body_measurements: Số đo cơ thể (ngực, eo, vai, hông).
            size_chart: Bảng thông số kỹ thuật của sản phẩm.
            current_trial_specs: Thông số chiếc áo cụ thể đang thử trên 3D.
            fit_diagnostics: Kết quả chẩn đoán vùng từ 3D Mesh.
            garment_category: 'tshirt', 'shirt', 'jacket', 'trousers'.
            fit_preference: 'regular', 'slim', 'oversized'.

        Returns:
            Dictionary chứa 'reply', 'is_refusal', 'source' ('gemini_llm', 'rule_fallback', 'cache').
        """
        # Bước 1: Kiểm tra Domain Guardrails (Chặn 100% câu hỏi ngoài lề / injection)
        is_allowed, refusal_msg = self.guardrail.is_query_allowed(user_query)
        if not is_allowed:
            return {
                "reply": refusal_msg,
                "is_refusal": True,
                "source": "domain_guardrail",
            }

        # Bước 2: Chuẩn bị thông tin người dùng
        profile = self.advisor.estimator.estimate_measurements(
            height_cm=height_cm,
            weight_kg=weight_kg,
            exact_measurements=body_measurements,
        )

        context_hash = self._make_context_hash(profile, size_chart, garment_category)

        # Bước 3: Kiểm tra Cache (LRU Response Cache)
        cached_reply = self.cache.get(user_query, context_hash=context_hash)
        if cached_reply:
            return {
                "reply": cached_reply,
                "is_refusal": False,
                "source": "lru_cache",
            }

        # Bước 4: Điều tiết tần suất truy cập (Concurrency Governor)
        await self.governor.acquire()
        try:
            # Thử gọi Gemini LLM nếu có API Key
            if self.api_key:
                prompt = build_stylist_context_prompt(
                    user_query=user_query,
                    user_profile=profile,
                    size_chart=size_chart,
                    current_trial_specs=current_trial_specs,
                    fit_diagnostics=fit_diagnostics,
                    garment_category=garment_category,
                    fit_preference=fit_preference,
                )
                loop = asyncio.get_event_loop()
                reply = await loop.run_in_executor(None, self._call_gemini_rest_api, prompt)
                source = "gemini_llm"
            else:
                # Tự động Fallback sang Rule-based Stylist
                reply = self._generate_rule_based_advice(
                    user_query=user_query,
                    user_profile=profile,
                    size_chart=size_chart,
                    fit_diagnostics=fit_diagnostics,
                    garment_category=garment_category,
                    fit_preference=fit_preference,
                )
                source = "rule_based_fallback"
        except Exception:
            # Zero-Crash: Bất kỳ lỗi mạng / timeout / quota nào cũng fallback an toàn
            reply = self._generate_rule_based_advice(
                user_query=user_query,
                user_profile=profile,
                size_chart=size_chart,
                fit_diagnostics=fit_diagnostics,
                garment_category=garment_category,
                fit_preference=fit_preference,
            )
            source = "exception_fallback"
        finally:
            self.governor.release()

        # Lưu câu trả lời vào Cache để phục vụ cho các request tiếp theo
        self.cache.set(user_query, reply, context_hash=context_hash)

        return {
            "reply": reply,
            "is_refusal": False,
            "source": source,
        }

    def ask(
        self,
        user_query: str,
        height_cm: float = 170.0,
        weight_kg: float = 65.0,
        body_measurements: Optional[Dict[str, float]] = None,
        size_chart: Optional[Dict[str, Dict[str, float]]] = None,
        current_trial_specs: Optional[Dict[str, Any]] = None,
        fit_diagnostics: Optional[Dict[str, Any]] = None,
        garment_category: str = "tshirt",
        fit_preference: str = "regular",
    ) -> Dict[str, Any]:
        """Tư vấn kích cỡ và form dáng đồng bộ (Synchronous Wrapper)."""
        return asyncio.run(
            self.ask_async(
                user_query=user_query,
                height_cm=height_cm,
                weight_kg=weight_kg,
                body_measurements=body_measurements,
                size_chart=size_chart,
                current_trial_specs=current_trial_specs,
                fit_diagnostics=fit_diagnostics,
                garment_category=garment_category,
                fit_preference=fit_preference,
            )
        )
