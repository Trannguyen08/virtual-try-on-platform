# RULE 05: CHANGE IMPACT LOG (QUY TẮC NHẬT KÝ TÁC ĐỘNG THAY ĐỔI)

> **Phạm vi áp dụng:** Áp dụng bắt buộc cho toàn bộ Agent ở mọi Role (M1, M2, M3, M4, M5) trong Virtual Try-On Platform.

---

## 1. Mục đích & Điều kiện Kích hoạt (Activation Criteria)
Nhật ký Tác động Thay đổi (**Change Impact Log**) là cơ chế bắt buộc nhằm kiểm soát rủi ro, chống phá vỡ hợp đồng giao tiếp giữa 5 phân hệ và duy trì tính minh bạch xuyên suốt dự án.

### 1.1. Khi nào BẮT BUỘC ghi Log?
- **Kích hoạt:** Sau mỗi đợt Agent thực hiện thêm mới, chỉnh sửa hoặc xóa code, file cấu hình, schema hoặc contract, **TRƯỚC KHI** báo hoàn thành công việc cho User.
- Agent phụ trách Role hiện tại (M1, M2, M3, M4 hoặc M5) bắt buộc gọi Skill [.agents/skills/change-impact-log/SKILL.md](file:///d:/Năm%204%20-%20Kỳ%201/Project/virtual-tryon/virtual-try-on-platform/.agents/skills/change-impact-log/SKILL.md) và tạo 01 file log mới cho đợt thay đổi đó.

### 1.2. Khi nào KHÔNG kích hoạt Log?
- Các phiên làm việc chỉ dừng ở mức: Đọc hiểu codebase, thảo luận kỹ thuật, giải thích code, hoặc đề xuất phương án thiết kế nhưng **chưa thực hiện ghi/sửa file**.
- **Chống lặp đệ quy:** Hành động tạo chính file nhật ký impact log **không kích hoạt** việc tạo log thứ hai.

---

## 2. Quyền hạn Ngoại lệ về Thư mục Ghi (Scope Exception)
- Theo quy định phân quyền, mỗi Role chỉ được ghi file trong thư mục của mình. Tuy nhiên, để phục vụ việc ghi nhật ký, **tất cả các Role (M1 đến M5) được cấp quyền ngoại lệ để tạo file mới trong thư mục**:
  ```text
  docs/change-logs/**
  ```
- *Lưu ý nghiêm ngặt:* Ngoại lệ này **chỉ áp dụng duy nhất cho việc tạo file log**. Tuyệt đối không được lợi dụng ngoại lệ này để sửa code, xóa tài liệu hoặc can thiệp ra ngoài phạm vi sở hữu của Role.

---

## 3. Quy trình 5 Bước Bắt buộc Thực hiện

1. **Chốt danh sách file thực tế:** Xác định chính xác danh sách các file đã thêm mới, sửa đổi hoặc xóa trong đợt làm việc. Không suy đoán; ghi rõ đường dẫn tương đối từ gốc repo.
2. **Đánh giá Tác động Đa chiều (Impact Analysis):**
   - **API & Contract:** Có thay đổi endpoint, Pydantic schema, tham số đầu vào/đầu ra nào không?
   - **Đơn vị & Hệ trục:** Có duy trì đúng chuẩn nội bộ (Mét) và hiển thị (Centimet), hệ trục Y-up không?
   - **Dữ liệu & Model:** Có tạo file nặng (> 50MB, trọng số, cache) cần bảo vệ chống commit không?
   - **Ảnh hưởng chéo giữa các Module:** Thay đổi này có tác động tới module nào khác (M1, M2, M3, M4, M5)? Nếu thiếu thông tin để xác thực, phải ghi rõ *"Chưa kiểm tra"* thay vì tự giả định an toàn.
3. **Quy chuẩn Đặt tên File Log:**
   - Định dạng tên file:
     ```text
     docs/change-logs/YYYYMMDD_HHMMSS_<ROLE>_<short_description>.md
     ```
   - **Thời gian:** Bắt buộc lấy theo múi giờ **Asia/Saigon (UTC+7)**.
   - **ROLE:** Mã vai trò thực hiện (`M1`, `M2`, `M3`, `M4`, hoặc `M5`).
   - Tuyệt đối không ghi đè lên các file log cũ đã có.
4. **Ghi nhận Hiện trạng Kiểm thử:**
   - Dựa trên bằng chứng có thật: Ghi rõ các test case đã chạy và trạng thái (PASS/FAIL).
   - Nếu Agent không được quyền chạy lệnh terminal và User chưa cung cấp log kiểm thử, bắt buộc ghi rõ: *"Chưa chạy test (Chờ User xác nhận)"*.
5. **Kế hoạch Bàn giao & Bước tiếp theo:**
   - Ghi rõ ai/module nào là người nhận bàn giao tiếp theo.
   - Liệt kê các việc còn tồn đọng hoặc khuyến nghị rủi ro.
