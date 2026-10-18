---
name: m1-body-expert
description: Chuyên môn kỹ thuật về Thị giác máy tính, SMPL-X 3D Body Parametric Model và Trích xuất số đo nhân trắc học cho Module M1 trong Virtual Try-On Platform.
---

# M1 BODY & MEASUREMENTS EXPERT SKILL

## 1. Bản chất Kiến trúc M1 (From 2D Image to 3D Measured Avatar)
Module M1 có nhiệm vụ chuyển đổi ảnh chân dung người dùng (2D) thành mô hình cơ thể 3D hình học chính xác (SMPL-X) và trích xuất bộ thông số nhân trắc học:

```text
┌────────────────────────┐
│  Ảnh người dùng (2D)   │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  Tiền xử lý ảnh        │ (Resize, Crop, rembg background removal)
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  MediaPipe Pose        │ (33 Keypoints 2D + Confidence)
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  SMPL-X Optimizer      │ (Khớp Shape β và Pose θ với Keypoints + Chiều cao)
└───────────┬────────────┘
            │
            ├──────────────────────────────────────────┐
            ▼                                          ▼
┌────────────────────────┐                 ┌────────────────────────┐
│  Xuất 3D Mesh          │                 │  Mesh Slicing Engine   │
│  (10.475 đỉnh, Y-up)   │                 │  (Cắt lớp tính số đo)  │
└───────────┬────────────┘                 └───────────┬────────────┘
            │ body.glb                                 │
            ▼                                          ▼
     [Cung cấp M2, M5]                    5 Số đo: Height, Chest,
                                          Waist, Hip, Shoulder (cm)
                                          [Cung cấp M3, M4]
```

---

## 2. Phương pháp luận Kỹ thuật Cốt lõi

### 2.1. Khớp mô hình tham số SMPL-X
- **Mô hình SMPL-X:** Sử dụng 10.475 đỉnh (vertices), tham số hình dạng $\beta \in \mathbb{R}^{10}$ (Shape parameters) và tư thế $\theta$ (Pose parameters).
- **Hàm mất mát tối ưu (Optimization Loss):**
  $$L_{total} = w_{kp} L_{keypoints} + w_{prior} L_{shape\_prior} + w_{height} L_{height}$$
- **Hệ trục tọa độ xuất file:** Bắt buộc chuẩn hóa về **Y-up, +Z forward**, đơn vị **Mét (m)**, không chứa tọa độ `NaN` hay `Inf`.

### 2.2. Trích xuất số đo qua Cắt lớp Mesh (Mesh Slicing)
- Tuyệt đối không dùng bounding box thô sơ để tính số đo.
- Sử dụng mặt phẳng cắt song song với mặt phẳng XZ (mặt phẳng nằm ngang) tại các mốc giải phẫu xác định:
  - **Chest/Bust:** Đi qua mốc nách/ngực (khoảng $y \approx 0.72 \times \text{Chiều cao}$).
  - **Waist:** Điểm thắt hẹp nhất ở phần bụng (khoảng $y \approx 0.58 \times \text{Chiều cao}$).
  - **Hip:** Điểm lồi rộng nhất ở xương chậu (khoảng $y \approx 0.50 \times \text{Chiều cao}$).
- **Chu vi lát cắt:** Tìm giao tuyến giữa mặt phẳng cắt và các tam giác mesh, sắp xếp các đoạn thẳng thành đa giác kín (Convex Hull hoặc Spline) và tính tổng độ dài chu vi.
- Sai số cho phép: lệch <= 1.0 cm so với tính toán giải tích chuẩn.

---

## 3. Xử lý Trường hợp Ngoại lệ (Edge Cases)
1. **Ảnh mất chân / mất đầu:** Bộ tiền xử lý phải trả về lỗi `INVALID_IMAGE` có kiểm soát, không được ném Exception làm sập luồng.
2. **Ảnh phong cảnh không có người:** MediaPipe không tìm thấy người phải trả về mã lỗi `NO_PERSON`.
3. **Người có dáng quá gầy hoặc quá béo:** Giới hạn khoảng giá trị nhân trắc học hợp lệ (Height: 140–210 cm, Chest: 60–140 cm, Waist: 50–130 cm, Hip: 70–150 cm). Nếu vượt ngưỡng, đưa ra cảnh báo độ tin cậy thấp và cho phép người dùng điều chỉnh tay.

---

## 4. Tài liệu Tham khảo Chuyên sâu (References)
Khi giải quyết các vấn đề kỹ thuật cụ thể, hãy tra cứu các tài liệu trong `references/`:
- [landmarks-and-slicing.md](references/landmarks-and-slicing.md): Chi tiết 33 keypoints MediaPipe và tọa độ cắt lớp 5 số đo.
- [smplx-specs.md](references/smplx-specs.md): Thông số kỹ thuật mô hình 10.475 đỉnh SMPL-X và tham số shape/pose.
- [edge-cases.md](references/edge-cases.md): Cẩm nang xử lý các ảnh lỗi, che khuất hoặc tư thế bất thường.
