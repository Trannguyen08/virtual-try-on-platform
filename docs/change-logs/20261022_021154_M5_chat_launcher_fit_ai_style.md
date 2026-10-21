# Change Impact Log — Nút chat theo ảnh tham chiếu feature/fit-ai

- Thời điểm: 2026-10-22 02:11 Asia/Saigon
- Vai trò: M5 Frontend
- Mục đích: Chỉnh nút nổi “Trợ lý AI” theo ảnh người dùng cung cấp.

## File thay đổi

| File | Trước → Sau |
| --- | --- |
| `frontend/src/styles/aiChatWidget.css` | `.vfit-chat-fab` là nút lớn với viền và bóng nhẹ → viên thuốc cao tối thiểu 36 px, nền xanh đậm chuyển sắc, viền sáng, quầng sáng xanh, chữ nhỏ gọn và không xuống dòng; trạng thái hover có ánh sáng rõ hơn. |

## Tác động

- API/schema/đơn vị/hệ trục/database/asset: Không thay đổi; chỉ sửa CSS của nút mở chat.
- Module khác: Không thay đổi M1–M4. Logic chat Gemini và bố cục cửa sổ giữ theo đợt sửa trước.
- Xung đột đã xác nhận: Không có trong file sửa. Nguy cơ: chưa đối chiếu mã CSS gốc trên nhánh `feature/fit-ai`; chỉ đối chiếu ảnh tham chiếu do user gửi. Cần xem lại trực quan ở desktop/mobile.
- Tài nguyên nặng: Không tạo.

## Kiểm thử và bàn giao

- Chưa chạy test (Chờ User xác nhận) theo Rule 01. Chưa xác minh trực quan trong browser.
- M5 bàn giao để user tải lại frontend, kiểm tra kích thước, màu và vị trí nút ở màn hình hẹp/rộng.
