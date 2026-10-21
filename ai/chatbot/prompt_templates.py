"""Prompts for the Virtual Try-On assistant."""

from typing import Any, Dict, Optional


# Kept for older callers of DomainGuardrail; the chat endpoint no longer uses it.
STANDARD_REFUSAL_MESSAGE = (
    "Dạ em là Trợ lý Tư vấn Kích cỡ của Virtual Try-On Platform. "
    "Em chỉ có thể hỗ trợ anh/chị chọn size, kiểm tra độ vừa vặn và tư vấn form dáng trang phục thôi ạ! "
    "Anh/chị đang quan tâm đến sản phẩm nào để em tư vấn kích cỡ chuẩn nhất ạ?"
)

SYSTEM_INSTRUCTION_STYLIST = """Bạn là trợ lý AI của Virtual Try-On Platform. Hãy trả lời câu hỏi của người dùng bằng tiếng Việt tự nhiên, rõ ràng và ngắn gọn. Bạn có thể trả lời cả các câu hỏi ngoài lĩnh vực thời trang.

Khi tư vấn trang phục, hãy ưu tiên số đo, bảng size và kết quả thử đồ được cung cấp. Phân biệt số đo ước lượng với số đo thực tế. Không tự nhận đã kiểm tra sản phẩm, dữ liệu thời gian thực hoặc mô hình 3D khi chưa có dữ liệu tương ứng. Nếu thiếu dữ liệu để chọn size chính xác, hãy hỏi thêm thông tin cần thiết. Với câu hỏi về thời gian thực, hãy nói rõ khi bạn không có dữ liệu cập nhật."""


def build_stylist_context_prompt(
    user_query: str,
    user_profile: Optional[Dict[str, Any]] = None,
    size_chart: Optional[Dict[str, Dict[str, float]]] = None,
    current_trial_specs: Optional[Dict[str, Any]] = None,
    fit_diagnostics: Optional[Dict[str, Any]] = None,
    garment_category: str = "tshirt",
    fit_preference: str = "regular",
) -> str:
    """Attach available try-on context without inventing measurements."""
    context_lines = []
    if user_profile or size_chart or current_trial_specs or fit_diagnostics:
        context_lines.append("=== NGỮ CẢNH THỬ ĐỒ (chỉ dùng khi liên quan câu hỏi) ===")
        context_lines.append(f"- Loại trang phục: {garment_category.upper()}")
        context_lines.append(f"- Kiểu mặc mong muốn: {fit_preference.upper()}")

        if user_profile:
            for key, label in (
                ("height", "Chiều cao"),
                ("weight", "Cân nặng"),
                ("bust", "Vòng ngực"),
                ("waist", "Vòng eo"),
                ("hip", "Vòng hông"),
                ("shoulder", "Vai"),
            ):
                if key in user_profile:
                    unit = "kg" if key == "weight" else "cm"
                    context_lines.append(f"- {label}: {user_profile[key]} {unit}")
            context_lines.append("- Số đo có thể được hệ thống ước lượng từ chiều cao/cân nặng; không coi số đo ước lượng là số đo trực tiếp.")

        if size_chart:
            context_lines.append("- Bảng size sản phẩm:")
            for size_name, specs in size_chart.items():
                details = ", ".join(f"{key}={value} cm" for key, value in specs.items())
                context_lines.append(f"  + {size_name}: {details}")
        if current_trial_specs:
            context_lines.append(f"- Trang phục đang thử: {current_trial_specs}")
        if fit_diagnostics:
            context_lines.append(f"- Đánh giá độ vừa: {fit_diagnostics}")
        context_lines.append("=== HẾT NGỮ CẢNH ===")

    context_lines.append(f"CÂU HỎI CỦA KHÁCH HÀNG: {user_query}")
    return "\n".join(context_lines)
