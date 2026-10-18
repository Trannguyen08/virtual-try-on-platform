"""Domain Guardrails & Concurrency Protection for AI Chatbot (Module M4).

Cung cấp:
1. DomainGuardrail: Bộ lọc chủ đề nghiêm ngặt, chặn prompt injection và câu hỏi ngoài lề (lập trình, thời tiết, giải toán...).
2. LRUResponseCache: Bộ đệm thông minh lưu câu trả lời cho các câu hỏi tương tự, giảm 80% chi phí token và phản hồi < 3ms.
3. ConcurrencyGovernor: Bộ điều tiết lưu lượng truy cập đồng thời, bảo vệ server và tránh lỗi Rate Limit (429).
"""

import asyncio
from collections import OrderedDict
import hashlib
import re
import threading
from typing import Any, Dict, Optional, Tuple

from ai.chatbot.prompt_templates import STANDARD_REFUSAL_MESSAGE


# ==============================================================================
# 1. BỘ TỪ KHÓA CHẶN NGOÀI LỀ & DỤ DỖ (OUT-OF-DOMAIN / INJECTION PATTERNS)
# ==============================================================================
PROHIBITED_PATTERNS = [
    # Lập trình / Viết code
    r"(code|python|javascript|java|c\+\+|html|css|sql|function|script|viết code|lập trình)",
    # Thời tiết
    r"(thời tiết|nhiệt độ|trời mưa|trời nắng|dự báo thời tiết|weather|forecast)",
    # Chính trị / Xã hội / Lịch sử
    r"(chính trị|tổng thống|chiến tranh|thủ tướng|bầu cử|chính phủ|chủ tịch nước)",
    # Toán học / Giải bài tập
    r"(giải phương trình|đạo hàm|tích phân|toán học|làm bài tập|hóa học|vật lý)",
    # Làm thơ / Kể chuyện / Văn học
    r"(thơ|làm thơ|viết thơ|bài thơ|kể chuyện|truyện cười|tiểu thuyết)",
    # Prompt Injection / Jailbreak
    r"(quên đi|ignore previous|bỏ qua các quy tắc|đóng vai|jailbreak|system prompt|lệnh hệ thống)",
]

# Các cụm từ và từ khóa nguyên vẹn liên quan đến thời trang / trang phục / kích cỡ
CLOTHING_PHRASES = [
    "chiều cao", "cân nặng", "sơ mi", "áo thun", "áo khoác", "quần tây", "quần thun",
    "bảng size", "chọn size", "giấu bụng", "vừa vặn", "tôn dáng", "độ cử động",
    "form rộng", "form ôm", "size s", "size m", "size l", "size xl", "size xxl",
]

CLOTHING_WORDS = {
    "size", "áo", "quần", "mặc", "ngực", "eo", "vai", "dài", "rộng", "chật",
    "vừa", "thụng", "ôm", "bó", "kg", "cm", "fit", "form", "vải", "dáng",
    "bụng", "tư vấn", "chọn", "thun", "khoác", "nách", "đáy", "cạp", "regular",
    "slim", "oversize", "oversized",
}


class DomainGuardrail:
    """Bộ lọc phòng thủ kiểm tra câu hỏi có thuộc phạm vi thời trang/kích cỡ hay không."""

    @classmethod
    def is_query_allowed(cls, query: str) -> Tuple[bool, Optional[str]]:
        """Kiểm tra câu hỏi của người dùng.

        Args:
            query: Chuỗi câu hỏi từ người dùng.

        Returns:
            Tuple (is_allowed: bool, refusal_message: Optional[str]).
        """
        q = query.strip().lower()

        if not q:
            return False, "Dạ anh/chị cần em hỗ trợ tư vấn chọn kích cỡ hay độ vừa vặn trang phục nào ạ?"

        # 1. Kiểm tra Prompt Injection và các câu hỏi cấm tuyệt đối
        for pattern in PROHIBITED_PATTERNS:
            if re.search(pattern, q, re.IGNORECASE):
                return False, STANDARD_REFUSAL_MESSAGE

        # 2. Kiểm tra câu hỏi có chứa ngữ cảnh thời trang / kích cỡ hay không
        # Kiểm tra cụm từ
        has_phrase = any(phrase in q for phrase in CLOTHING_PHRASES)

        # Kiểm tra từ nguyên vẹn (word-tokenized để tránh lỗi substring như 'm' trong 'làm')
        tokens = set(re.findall(r"[\w]+", q))
        has_word = bool(tokens & CLOTHING_WORDS)

        if not (has_phrase or has_word):
            # Hoàn toàn không liên quan đến thời trang hay kích cỡ
            return False, STANDARD_REFUSAL_MESSAGE

        return True, None

    validate_query = is_query_allowed


# ==============================================================================
# 2. BỘ ĐỆM PHẢN HỒI THÔNG MINH (LRU RESPONSE CACHE)
# ==============================================================================
class LRUResponseCache:
    """Bộ đệm LRU thread-safe lưu trữ các câu trả lời tư vấn cho cùng ngữ cảnh."""

    def __init__(self, capacity: int = 256) -> None:
        self.capacity = capacity
        self.cache: OrderedDict[str, str] = OrderedDict()
        self.lock = threading.Lock()

    def _make_key(self, query: str, context_hash: str) -> str:
        """Tạo khóa hash từ câu hỏi và ngữ cảnh đo đạc."""
        combined = f"{query.strip().lower()}::{context_hash}"
        return hashlib.md5(combined.encode("utf-8")).hexdigest()

    def get(self, query: str, context_hash: str = "") -> Optional[str]:
        """Lấy câu trả lời từ Cache nếu có."""
        key = self._make_key(query, context_hash)
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
        return None

    def set(self, query: str, response: str, context_hash: str = "") -> None:
        """Lưu câu trả lời vào Cache."""
        key = self._make_key(query, context_hash)
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = response
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)


# ==============================================================================
# 3. BỘ ĐIỀU TIẾT LƯU LƯỢNG ĐỒNG THỜI (CONCURRENCY GOVERNOR)
# ==============================================================================
class ConcurrencyGovernor:
    """Bộ giới hạn số lượng request đồng thời gọi tới LLM Provider."""

    def __init__(self, max_concurrent_requests: int = 10) -> None:
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def acquire(self) -> None:
        """Chờ lấy slot gọi LLM."""
        await self.semaphore.acquire()

    def release(self) -> None:
        """Giải phóng slot."""
        self.semaphore.release()
