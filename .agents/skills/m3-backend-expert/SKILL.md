---
name: m3-backend-expert
description: Chuyên môn kỹ thuật về Thiết kế FastAPI RESTful API, Quản lý Tác vụ Bất đồng bộ (Async Job Manager) và Bộ điều phối Pipeline (Orchestrator) cho Module M3 trong Virtual Try-On Platform.
---

# M3 BACKEND, API & ORCHESTRATION EXPERT SKILL

## 1. Bản chất Kiến trúc M3 (The Core Orchestrator)
Module M3 đóng vai trò là "Nhạc trưởng điều phối" toàn bộ hệ thống Virtual Try-On, tiếp nhận yêu cầu từ Frontend và điều phối công việc giữa M1, M2, M4:

```text
               ┌───────────────────────┐
               │  Frontend Client (M5) │
               └───────────┬───────────┘
                           │ HTTP Request
                           ▼
               ┌───────────────────────┐
               │      FastAPI API      │
               │ (/analyze, /fit, ...) │
               └───────────┬───────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │ Pipeline Orchestrator │ ◄── Cờ APP_MODE (mock / real)
               └───────────┬───────────┘
                           │
      ┌────────────────────┼────────────────────┐
      ▼                    ▼                    ▼
┌───────────┐        ┌───────────┐        ┌───────────┐
│ Module M1 │        │ Module M2 │        │ Module M4 │
│ (Body)    │        │ (Garment) │        │ (Fit/AI)  │
└───────────┘        └───────────┘        └───────────┘
```

---

## 2. Phương pháp luận Kỹ thuật Cốt lõi

### 2.1. Thiết kế Endpoint & Hợp đồng Dữ liệu (Pydantic Contracts)
- Mọi request và response bắt buộc được định nghĩa thông qua Pydantic V2 models tại `shared/schemas/`.
- Phân tách rõ ràng giữa Response đồng bộ (Sync - cho các tác vụ tính toán nhanh như gợi ý size `/tryon/recommend` <= 1.0s) và Response bất đồng bộ (Async - cho mô phỏng Blender `/tryon/fit` mất nhiều phút):
  - Khi gọi `/tryon/fit`: Trả về ngay lập tức HTTP `202 Accepted` kèm JSON:
    ```json
    {
      "job_id": "job_123e4567-e89b-12d3-a456-426614174000",
      "status": "pending",
      "estimated_seconds": 180
    }
    ```
  - Frontend sau đó sẽ polling endpoint `GET /jobs/{id}` để cập nhật tiến độ cho đến khi `status: "completed"`.

### 2.2. Kiến trúc Orchestrator Decoupling (`APP_MODE`)
- Hệ thống hỗ trợ chuyển đổi chế độ hoạt động thông qua biến môi trường `APP_MODE`:
  - `APP_MODE = mock`: Mọi module (M1, M2, M4) đều dùng Mock implementation, trả dữ liệu giả lập chuẩn schema ngay lập tức, phục vụ test CI và phát triển Frontend.
  - `APP_MODE = real`: Kích hoạt module thật tương ứng khi module đó đã hoàn thành và vượt qua kiểm thử.
  - Hỗ trợ bật/tắt từng module riêng rẽ: `M1_MODE = real`, `M2_MODE = mock`, `M4_MODE = real`.

---

## 3. Xử lý Trường hợp Ngoại lệ (Edge Cases)
1. **Tiến trình mô phỏng Blender bị treo hoặc quá tải:** Job Manager phải có bộ hẹn giờ (Timeout watchdog). Nếu quá thời gian quy định (ví dụ 6 phút), tiến trình con phải bị buộc ngắt (kill process), cập nhật trạng thái job thành `failed` kèm mã lỗi `JOB_TIMEOUT`.
2. **Người dùng gửi file ảnh hỏng hoặc sai định dạng:** Bắt lỗi ngay tại tầng validation của FastAPI, trả về HTTP `422 Unprocessable Entity` hoặc `400 Bad Request` kèm message chi tiết, không truyền dữ liệu bẩn xuống M1.
3. **Đổi size nhiều lần liên tục:** Triển khai bộ nhớ đệm (In-memory LRU Cache hoặc Redis) lưu kết quả theo key `hash(body_mesh, garment_id, size)`. Nếu người dùng chuyển lại size đã mô phỏng trước đó, trả về kết quả ngay lập tức mà không chạy lại mô phỏng.

---

## 4. Tài liệu Tham khảo Chuyên sâu (References)
Khi giải quyết các vấn đề kỹ thuật cụ thể, hãy tra cứu các tài liệu trong `references/`:
- [api-endpoints-and-schemas.md](references/api-endpoints-and-schemas.md): Đặc tả chi tiết Endpoint và Pydantic schemas.
- [async-job-flow.md](references/async-job-flow.md): Vòng đời Job bất đồng bộ và cơ chế bộ nhớ đệm Caching.
- [error-codes.md](references/error-codes.md): Bảng mã lỗi hệ thống và ánh xạ HTTP status.
