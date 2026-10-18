# REFERENCE: ASYNC JOB LIFECYCLE & CACHING ARCHITECTURE (M3)

Đặc tả luồng xử lý tác vụ mô phỏng bất đồng bộ và kiến trúc bộ nhớ đệm (Caching) cho Module M3.

---

## 1. Vòng đời Trạng thái Job (Job Lifecycle)

```text
       [POST /tryon/fit]
               │
               ▼
       ┌───────────────┐
       │    pending    │  (Đã lưu Job vào Queue / In-memory registry)
       └───────┬───────┘
               │ Worker tiếp nhận
               ▼
       ┌───────────────┐
       │    running    │  (Đang chạy script Blender drape.py)
       └───────┬───────┘
               │
       ┌───────┴───────────────────────┐
       ▼                               ▼
┌───────────────┐               ┌───────────────┐
│   completed   │               │    failed     │ (Timeout hoặc lỗi mesh)
└───────────────┘               └───────────────┘
```

---

## 2. Chiến lược Bộ nhớ đệm (Caching Strategy)
Mô phỏng vải là tác vụ tốn kém CPU/GPU ($2 - 3\text{ phút}$). Do đó:
- **Cache Key:** `key = sha256(f"{body_id}:{garment_id}:{size}")`
- Khi người dùng gửi request `POST /tryon/fit`:
  1. Kiểm tra trong Cache xem key đã tồn tại và có file `draped.glb` chưa.
  2. Nếu **Cache Hit:** Trả về trạng thái `completed` kèm URL kết quả ngay lập tức ($< 0.1\text{ s}$).
  3. Nếu **Cache Miss:** Khởi tạo Job mới và đẩy vào luồng chạy nền.
