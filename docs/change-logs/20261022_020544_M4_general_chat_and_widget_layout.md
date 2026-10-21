# Change Impact Log — Trợ lý chat đa chủ đề và giao diện gọn

- Thời điểm: 2026-10-22 02:05 Asia/Saigon
- Vai trò: M4 (AI/chat API), M5 (frontend chat). User yêu cầu sửa đồng thời hai phần.
- Mục đích: Cho phép trả lời câu hỏi ngoài thời trang qua Gemini và sửa chữ tràn trong widget.

## File thay đổi

| File | Trước → Sau |
| --- | --- |
| `ai/chatbot/stylist_agent.py` | `FitStylistChatbot.ask_async` từ chối câu hỏi ngoài thời trang trước khi gọi Gemini, dùng mặc định 170 cm/65 kg và fallback lời khuyên size cho mọi lỗi → gửi mọi câu hỏi không rỗng tới Gemini, chỉ dùng số đo khi được cung cấp, fallback size khi có hồ sơ/bảng size/câu hỏi phù hợp; còn lại báo AI không khả dụng. Model lấy từ `GEMINI_MODEL` hoặc mặc định `gemini-3.8-flash`; REST API dùng header khóa, mức suy luận low cho model mặc định, timeout 30 giây và gom phần văn bản trả lời. Cache chỉ lưu câu trả lời Gemini thành công theo toàn bộ prompt. Lỗi Gemini chỉ log mã HTTP hoặc tên loại lỗi, không log khóa/câu hỏi. |
| `ai/chatbot/prompt_templates.py` | System prompt bắt buộc từ chối ngoài thời trang và prompt luôn gắn ngữ cảnh size → system prompt hỗ trợ câu hỏi chung, ngữ cảnh thử đồ chỉ xuất hiện khi có dữ liệu; không tự điền số đo mẫu. Hằng từ chối cũ giữ lại cho `DomainGuardrail` độc lập. |
| `ai/api/schemas.py` | `ChatStylistRequest.height_cm/weight_kg` mặc định số đo mẫu → mặc định `None`; mô tả `ChatStylistResponse` và `AiHealthResponse.guardrail_active` khớp luồng mới. |
| `ai/api/router.py` | Mô tả `/chat` và `/health` nói bộ lọc chủ đề đang hoạt động → mô tả trả lời chung, `guardrail_active=false`. |
| `frontend/src/components/chat/AiStylistChatWidget.tsx` | Gửi hồ sơ mẫu, avatar chứa chữ dài, nhãn từ chối chủ đề → chỉ gửi câu hỏi, tiêu đề ngắn, bỏ avatar và nhãn cũ. |
| `frontend/src/styles/aiChatWidget.css` | Header/close/launcher kích thước không đủ chữ, bong bóng có nguy cơ tràn → flex co đúng, văn bản xuống dòng, ô nhập co lại, chiều rộng di động phù hợp viewport. |
| `frontend/src/api/aiApi.ts` | Chú thích client nói chat bị lọc chủ đề → mô tả khả năng hỏi đáp chung. |
| `tests/unit/ai/test_chatbot.py` | Test bắt buộc từ chối câu hỏi ngoài thời trang → test chuyển câu hỏi chung qua Gemini giả lập và trường hợp AI thiếu khóa; fallback size dùng khóa rỗng để tránh gọi mạng. |
| `tests/unit/ai/test_ai_api.py` | Test endpoint bắt buộc từ chối và health báo guardrail bật → test phản hồi ngoài thời trang qua Gemini giả lập, health báo guardrail tắt. |

## Tác động

- API: Giữ endpoint và trường response; `height_cm`/`weight_kg` khi vắng mặt nay là `None`, không còn gán 170 cm/65 kg. `source` có thể là `ai_unavailable`, `guardrail_active` đổi sang false. Client cũ gửi số đo tường minh vẫn tương thích.
- Schema/đơn vị: Số đo ngoại vi vẫn là cm/kg; không đụng hệ trục hay mesh.
- Database/asset/model file: Không thay đổi, không tạo file nặng.
- Ảnh hưởng M4–M5: Widget chỉ gửi `query`; backend tự phân biệt không có hồ sơ. `DomainGuardrail` độc lập còn tồn tại nhưng không chạy trong endpoint chat.
- Xung đột đã xác nhận: Test cũ yêu cầu từ chối ngoài thời trang trái với yêu cầu mới; đã cập nhật hai test endpoint/chatbot. Nguy cơ: khóa/model/quota Gemini không hợp lệ thì câu hỏi chung chỉ nhận thông báo tạm thời không kết nối; chưa xác minh qua API thật.

## Kiểm thử và bàn giao

- Chưa chạy test (Chờ User xác nhận); quy tắc repo không cho agent chạy terminal/test. Đã đối chiếu tĩnh caller, schema, CSS và cập nhật test hồi quy `TC-AI-CHAT-01` đến `TC-AI-CHAT-03`.
- User cần khởi động lại backend, tải lại frontend và thử một câu hỏi ngoài thời trang cùng một câu hỏi chọn size. M4 kiểm tra log Gemini nếu hiện `ai_unavailable`; M5 kiểm tra giao diện ở viewport hẹp và rộng.
