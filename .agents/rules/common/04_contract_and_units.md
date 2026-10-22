# RULE 04: CONTRACT FIRST, UNIT & COORDINATE SYSTEM (COMMON)

> **Phạm vi áp dụng:** Áp dụng bắt buộc cho toàn bộ Agent ở mọi Role (M1, M2, M3, M4, M5).

---

## 1. Nguyên tắc "Contract First" (Hợp đồng là Tối thượng)
Agent tuyệt đối không viết code dựa trên phỏng đoán dữ liệu của module khác:
- Quy trình xử lý dữ liệu giữa các module luôn tuân thủ:
  ```text
  Input Schema Validation → Core Processing → Output Schema Validation
  ```
- **Phát triển độc lập qua Mock:** Trong khi các module bạn chưa có output thật, mỗi module sử dụng **Mock Contract** (`shared/interfaces` và `shared/schemas`) để hoàn thiện 100% logic nội bộ và test unit. Không được chờ đợi output của nhau.
- **Cấm Silent Fix:** Khi tích hợp dữ liệu thật, nếu phát hiện đầu ra của module khác sai schema hoặc lỗi logic, **BẮT BUỘC BÁO LỖI**, tuyệt đối không tự viết code âm thầm vá ngầm (Silent Fix) để thỏa hiệp với lỗi của module khác.

---

## 2. Tiêu chuẩn Đơn vị & Hệ trục Tọa độ Toàn dự án (Project Standard)
Mọi phép tính toán học, sinh mesh 3D, mô phỏng vải, và rendering bắt buộc phải đồng bộ hệ quy chiếu:

| Thuộc tính | Quy định Nội bộ (Internal Standard) | Quy định Ngoại vi (API / Display) | Quy tắc chuyển đổi |
| :--- | :--- | :--- | :--- |
| **Đơn vị đo dài (Length/Distance)** | **Mét (m)** | **Centimet (cm)** | 1 m = 100 cm |
| **Hệ tọa độ (Coordinate System)** | **Right-handed (Tay phải)** | **Right-handed** | Đồng bộ Three.js & Blender |
| **Trục đứng (Up-Axis)** | **Y-up** (Theo chuẩn SMPL-X) | **Y-up** | Three.js mặc định Y-up |
| **Trục nhìn (Forward-Axis)** | **+Z forward** | **+Z forward** | Giữ nguyên |

*Cấm tuyệt đối mọi phép tính khoảng cách hay ghép mesh giữa các module nếu chưa chuẩn hóa về cùng đơn vị (m) và hệ trục (Y-up).*

---

## 3. Quy trình Thay đổi Quyết định (Change Control Process)
Nếu trong quá trình làm việc, Agent phát hiện hợp đồng (Pydantic schema, JSON format), đơn vị đo hoặc ngưỡng phân loại có điểm bất hợp lý cần cải tiến, Agent **BẮT BUỘC** tuân thủ quy trình:
1. **Mô tả Vấn đề (Problem):** Chỉ rõ điểm bất cập ở đâu, tại file nào.
2. **Phân tích Ảnh hưởng (Impact Analysis):** Liệt kê chính xác các module nào (M1, M2, M3, M4, M5) sẽ bị ảnh hưởng nếu thay đổi.
3. **Đề xuất Giải pháp (Proposed Change):** Trình bày phương án sửa đổi kèm schema mới.
4. **User Phê duyệt:** Chỉ thực hiện sửa đổi khi User đồng ý.
