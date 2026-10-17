---
name: change-impact-log
description: Hướng dẫn quy trình, cấu trúc mẫu biểu và cách ghi Nhật ký Tác động Thay đổi (Change Impact Log) sau mỗi đợt sửa đổi code/config/contract cho mọi Role (M1 đến M5).
---

# CHANGE IMPACT LOG SKILL

## 1. Mục đích
Skill này hướng dẫn Agent cách khởi tạo và điền nội dung vào một file **Change Impact Log** tại `docs/change-logs/` trước khi thông báo hoàn thành nhiệm vụ với User, theo đúng quy định tại [05_change_impact_log.md](file:///d:/Năm%204%20-%20Kỳ%201/Project/virtual-tryon/virtual-try-on-platform/.agents/rules/common/05_change_impact_log.md).

---

## 2. Quy tắc Đặt tên File Log
- Đường dẫn: `docs/change-logs/`
- Tên file: `YYYYMMDD_HHMMSS_<ROLE>_<ten_ngan_gon>.md`
- **Quy định thời gian:** Phải lấy giờ địa phương Việt Nam (**Asia/Saigon, UTC+7**).
- **ROLE:** Viết hoa một trong 5 mã: `M1`, `M2`, `M3`, `M4`, `M5`.
- *Ví dụ:* `docs/change-logs/20261017_140500_M4_random_forest_v1_pipeline.md`

---

## 3. Khung Mẫu Chuẩn (Standard Log Template)

Khi tạo file log mới, Agent **BẮT BUỘC** sử dụng cấu trúc chuẩn sau:

```markdown
# CHANGE IMPACT LOG

- **Thời gian (Asia/Saigon):** YYYY-MM-DD HH:MM:SS
- **Role thực hiện:** M1 | M2 | M3 | M4 | M5
- **Nhánh Git:** feature/...
- **Tác vụ liên quan:** [Mã Task: ví dụ BOD-01, GAR-04, API-03, AI-04, WEB-01]

---

## 1. Danh sách File Thay đổi
- `[ADDED]` đường/dẫn/file_moi.py — Mô tả ngắn gọn công dụng
- `[MODIFIED]` đường/dẫn/file_sua.py — Mô tả các chỉnh sửa chính
- `[DELETED]` đường/dẫn/file_xoa.py — Lý do xóa

---

## 2. Đánh giá Tác động Kỹ thuật (Technical Impact Analysis)

| Khía cạnh | Có ảnh hưởng? | Chi tiết phân tích & Đánh giá rủi ro |
| :--- | :---: | :--- |
| **API & Schema Contract** | Có / Không | Thay đổi trường dữ liệu nào trong Pydantic / JSON schema? Có gây vỡ tương thích ngược không? |
| **Đơn vị & Hệ tọa độ** | Chuẩn hóa | Đã tuân thủ Mét (nội bộ), Centimet (ngoại vi), hệ trục Y-up, +Z forward chưa? |
| **Tài nguyên nặng (>50MB)** | Không / Cảnh báo | Có phát sinh model weights, file mảng numpy, dữ liệu lớn cần chặn commit không? |
| **Tác động chéo Module** | M1/M2/M3/M4/M5 | Module khác có cần cập nhật theo thay đổi này không? (Nếu thiếu thông tin, ghi "Chưa kiểm tra"). |

---

## 3. Trạng thái Kiểm thử (Verification & Testing)
- **Lệnh kiểm thử liên quan:** `pytest tests/... -v`
- **Kết quả thực tế:**
  - [x] Đã chạy trên máy User: `XX passed, 0 failed` (Kèm bằng chứng log).
  - [ ] Chưa chạy kiểm thử (Chờ User chạy và xác nhận).

---

## 4. Kế hoạch Bàn giao & Bước tiếp theo (Next Steps)
- **Người / Module nhận bàn giao:** [Ví dụ: M3 Backend hoặc M5 Frontend]
- **Công việc tiếp theo:** [Nêu rõ 1-2 đầu việc cần làm ngay sau đợt này]
- **Cảnh báo tồn đọng:** [Ghi nhận các điểm lưu ý hoặc nợ kỹ thuật (nếu có)]
```

---

## 4. Lưu ý Nghiêm ngặt
1. **Tính trung thực:** Nếu chưa kiểm tra tác động chéo tới module khác, phải ghi rõ *"Chưa kiểm tra"* — tuyệt đối không được tự suy đoán hoặc khẳng định bừa.
2. **Không ghi dữ liệu nhạy cảm:** Không ghi API keys, token, mật khẩu, dữ liệu cá nhân vào log.
3. **Chống vòng lặp:** Sau khi tạo file log này xong, **dừng lại và báo cáo với User**, không tự kích hoạt thêm lần tạo log nào nữa.
