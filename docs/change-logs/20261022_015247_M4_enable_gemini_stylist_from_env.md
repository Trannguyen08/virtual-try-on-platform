# Change Impact Log: Nạp Gemini API key cho AI Stylist

## Vai trò và mục đích

- Vai trò: M4 (AI Stylist).
- Mục đích: để chatbot nhận `GEMINI_API_KEY` từ `.env` trước khi singleton chatbot khởi tạo và dùng Gemini cho câu hỏi thời trang.
- Thời gian: 2026-10-22 01:52 Asia/Saigon.
- Không ghi giá trị bí mật của API key vào log hoặc memory.

## File thay đổi

- `.env`: thêm biến `GEMINI_API_KEY` do user cung cấp; không ghi lại giá trị tại đây.
- `.gitignore`: bỏ comment dòng `.env` để các lần thêm mới không đưa file bí mật vào Git. Nếu file đã được Git theo dõi trước đó, quy tắc ignore không tự gỡ file khỏi index; trạng thái này chưa kiểm tra vì không chạy Git.
- `.env.example`: thêm dòng `GEMINI_API_KEY=` trống và `GEMINI_MODEL=gemini-3.8-flash` để hướng dẫn cấu hình mà không lộ key.
- `ai/chatbot/stylist_agent.py`: nạp `.env` từ thư mục gốc trước khi tạo `FitStylistChatbot`; cho phép chọn model qua `GEMINI_MODEL`; mặc định chuyển từ `gemini-1.5-flash` sang `gemini-3.8-flash`.

## Ảnh hưởng

- API/schema: không đổi endpoint hoặc contract. Frontend tiếp tục gọi `/api/v1/ai/chat`.
- Hành vi AI: khi có key hợp lệ và Gemini API truy cập được, câu hỏi thời trang sẽ được gửi tới Gemini. Bộ lọc chủ đề vẫn từ chối câu ngoài phạm vi; nếu Gemini lỗi, cơ chế rule-based fallback hiện có vẫn được dùng.
- Đơn vị/hệ trục: không áp dụng; không thay đổi.
- Database/asset/model weights: không thay đổi.
- Module: thay đổi trong M4; frontend và backend route không đổi.
- Phụ thuộc ngoài: yêu cầu API key hợp lệ, quyền gọi Gemini API và kết nối mạng.
- Xung đột đã xác nhận: không. Rủi ro còn lại: khóa có thể sai/hết hiệu lực hoặc model không được cấp quyền; chưa kiểm tra trực tiếp.

## Kiểm thử

- Đã kiểm tra an toàn bằng lệnh chỉ đọc rằng biến có mặt trong `.env`, file `.env` được ignore, và tên model/loader nằm trong code. Không in giá trị key.
- Chưa chạy backend, test hay gửi request Gemini theo Rule 01. Chưa xác nhận API key hợp lệ hoặc quyền truy cập model.

## Bàn giao

- Owner tiếp theo: user/M4. Khởi động lại backend để biến môi trường mới được nạp, sau đó thử một câu hỏi về size. Backend cần được restart sau thay đổi `.env`.
- Khóa đã được dán trong hội thoại; nên thu hồi và tạo khóa mới sau khi xác nhận luồng hoạt động. Không gửi khóa mới trong chat; thay trực tiếp trong `.env`.
