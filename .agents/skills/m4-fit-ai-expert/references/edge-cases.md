# REFERENCE: EDGE CASES & EXCEPTION HANDLING (XỬ LÝ TRƯỜNG HỢP BIÊN)

Tài liệu này tổng hợp các trường hợp dị biệt và chiến lược xử lý an toàn để đảm bảo hệ thống Module M4 không bao giờ bị Crash (Zero-Crash Policy).

---

## 1. Dị biệt Hình học 3D (3D Mesh Anomalies)

### 1.1. Mesh Rỗng hoặc File Hỏng (Empty / Corrupted Mesh)
- **Tình huống:** File `.glb` hoặc `.obj` không có đỉnh (`vertex_count == 0`) hoặc không có mặt (`face_count == 0`).
- **Xử lý:** Kiểm tra ngay tại lớp validation đầu vào; ném ra exception cụ thể `InvalidMeshException("Mesh has no vertices or faces")`, trả về mã lỗi rõ ràng cho Backend thay vì để chương trình sập do chia cho 0.

### 1.2. Đỉnh chứa Giá trị Bất thường (NaN / Inf Coordinates)
- **Tình huống:** Do quá trình mô phỏng Blender bị vỡ hạt, một số đỉnh có tọa độ là `NaN` hoặc `+/- Infinity`.
- **Xử lý:** Quét kiểm tra `np.isnan(vertices).any()` và `np.isinf(vertices).any()`. Nếu phát hiện, từ chối tính toán ngay lập tức và ghi log báo cáo lỗi cho M2 (không tự ý xóa đỉnh làm sai topology).

### 1.3. Mặt bị Đảo Pháp tuyến (Inverted Normals)
- **Tình huống:** Pháp tuyến mặt ngoài của áo quay vào trong, làm sai lệch dấu của Signed Distance (tính nhầm ngoài thành trong).
- **Xử lý:** Sử dụng `trimesh.repair.fix_normals()` trước khi tính toán khoảng cách xuyên thấu.

---

## 2. Dị biệt Dữ liệu & AI (Data & Machine Learning Anomalies)

### 2.1. Thiếu Trường Số đo Cơ thể (Missing Features)
- **Tình huống:** Người dùng chỉ nhập chiều cao, thiếu số đo ngực hoặc eo.
- **Xử lý:** 
  1. Nếu model AI có cơ chế imputer: điền bằng giá trị trung vị (median) theo tỷ lệ chiều cao/cân nặng chuẩn.
  2. Nếu không đủ độ tin cậy: Tự động chuyển sang Rule-based Baseline và hạ điểm `confidence`.

### 2.2. Người mẫu Ngoại cỡ hoặc Dáng người Dị biệt (Extreme Body Shapes)
- **Tình huống:** Chiều cao $< 130\text{ cm}$ hoặc $> 220\text{ cm}$, vòng ngực vượt quá dải Size Chart.
- **Xử lý:** Hệ thống không gán size ép buộc; trả về size lớn nhất/nhỏ nhất kèm cờ cảnh báo `out_of_chart_range = True`.

---

## 3. Chiến lược Dự phòng Bắt buộc (Graceful Fallback Mechanism)

```text
┌───────────────────────────────────────┐
│        Yêu cầu Tính toán Độ vừa       │
└──────────────────┬────────────────────┘
                   ▼
┌───────────────────────────────────────┐
│    Kiểm tra Trạng thái Mô hình AI    │
└──────────────────┬────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
    [AI Sẵn sàng]       [AI Gặp sự cố]
         │              (Mất file weights, thiếu PyTorch, lỗi inference)
         │                   │
         ▼                   ▼
┌─────────────────┐ ┌─────────────────────────────────────────┐
│ AI Inference    │ │ KÍCH HOẠT FALLBACK VỀ GEOMETRY BASELINE │
│ (Dự đoán điểm)  │ │ (Tính điểm bằng công thức giải tích)    │
└────────┬────────┘ └────────────────────┬────────────────────┘
         │                               │
         └───────────────┬───────────────┘
                         ▼
┌────────────────────────────────────────────────────────┐
│ Phản hồi Kết quả An toàn (Ghi log cảnh báo nếu có lỗi) │
└────────────────────────────────────────────────────────┘
```

- **Quy tắc vàng:** Cho dù GPU mất kết nối, file weights `.pt` bị xóa, hay model dự đoán ra lỗi cú pháp, **hệ thống M4 luôn phải trả về kết quả từ Geometry Baseline** kèm log cảnh báo. Tuyệt đối không để crash luồng chính của Backend.
