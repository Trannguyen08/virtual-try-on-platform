# REFERENCE: FRONTEND UX FLOWS & CLIENT STATE MANAGEMENT (M5)

Đặc tả luồng tương tác người dùng (User Experience) và quản lý trạng thái giao diện cho Module M5.

---

## 1. Luồng Trải nghiệm Người dùng (Step-by-Step Flow)

```text
[BƯỚC 1: UPLOAD]
Người dùng tải ảnh chân dung + nhập chiều cao (tùy chọn)
        │
        ▼
[BƯỚC 2: ANALYZE PROGRESS]
Hiển thị thanh tiến trình / skeleton loading trong khi chờ M1 trích xuất số đo
        │
        ▼
[BƯỚC 3: PHÒNG THỬ ĐỒ 3D]
Three.js tải body.glb, hiển thị bảng 5 số đo và danh sách áo
        │
        ▼
[BƯỚC 4: CHỌN ÁO & THỬ SIZE]
Người dùng chọn áo + size (S/M/L/XL)
  ├─ Nếu kết quả có trong Cache → Hiển thị ngay lập tức
  └─ Nếu chưa có → Hiển thị spinner "Đang mô phỏng vải..." + Polling GET /jobs/{id} mỗi 2s
        │
        ▼
[BƯỚC 5: XEM KẾT QUẢ VỪA VẶN & HEATMAP]
Hiển thị điểm Fit Score, nút bật/tắt Heatmap màu 3D, và size khuyến nghị từ AI
```

---

## 2. Nguyên tắc Phòng ngừa Lỗi Giao diện (Zero-Crash UI)
1. **Fallback Mock Data:** Nếu kết nối tới Backend API bị mất (Network Error), tự động chuyển sang chế độ Demo Mode dùng dữ liệu mock để người dùng vẫn trải nghiệm được giao diện mà không bị đơ.
2. **Không chặn giao diện (Non-blocking UI):** Các tác vụ tải mesh 3D phải chạy bất đồng bộ với thanh tiến trình rõ ràng (Progress bar từ `GLTFLoader.onProgress`).
3. **Phản hồi tức thì:** Khi bấm nút đổi size, giao diện phải phản hồi ngay lập tức (hiển thị trạng thái active ở nút bấm) trước khi nhận kết quả từ server.
