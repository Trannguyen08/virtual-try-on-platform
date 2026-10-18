---
name: m2-garment-expert
description: Chuyên môn kỹ thuật về Tạo dựng Mesh Quần áo 3D, Hệ thống Size Chart và Mô phỏng Vật lý Vải (Cloth Simulation) bằng Blender bpy headless cho Module M2 trong Virtual Try-On Platform.
---

# M2 GARMENT & CLOTH SIMULATION EXPERT SKILL

## 1. Bản chất Kiến trúc M2 (From 3D Template to Draped Simulation)
Module M2 đảm nhận việc quản lý dữ liệu trang phục 3D, phóng to/thu nhỏ theo bảng size chart và thực hiện mô phỏng vải rơi (Draping) ôm sát cơ thể người:

```text
┌────────────────────────┐
│  3D Garment Template   │ (T-shirt/Shirt, Topology sạch <= 30k vertices)
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  Size Chart Scaling    │ (Morphing ra 4 size S/M/L/XL theo bảng số đo)
└───────────┬────────────┘
            │ garment_size.obj
            ├──────────────────────────────────────────┐
            ▼                                          │
┌────────────────────────┐                             │
│  Blender bpy Headless  │ ◄─── body.obj (từ M1)       │
│  (Cloth + Collision)   │                             │
└───────────┬────────────┘                             │
            │                                          │
            ▼                                          │
┌────────────────────────┐                             ▼
│  draped.glb / .obj     │                   [Cung cấp M3, M4 để
│  (Khớp Y-up, Mét)      │                    so sánh kích thước]
└───────────┬────────────┘
            │
            ▼
     [Cung cấp M4 (Tính Fit),
      M5 (Hiển thị Three.js)]
```

---

## 2. Phương pháp luận Kỹ thuật Cốt lõi

### 2.1. Cấu hình Vật lý Vải (Blender Cloth Simulation)
Khi chạy Blender ở chế độ không giao diện (`blender --background --python drape.py`), thiết lập các thông số mô phỏng chuẩn mực:
- **Cloth Modifier:**
  - `mass`: $0.15 - 0.25\text{ kg/m}^2$ (vải cotton tiêu chuẩn).
  - `tension_stiffness`: $15 - 25$ (độ cứng co dãn).
  - `compression_stiffness`: $15 - 20$ (độ cứng nén).
  - `bending_stiffness`: $0.5 - 1.2$ (độ uốn mềm mại tự nhiên).
  - `damping`: $5.0$ (triệt tiêu dao động dư thừa nhanh chóng).
- **Collision Modifier trên Body:**
  - `distance`: $0.005\text{ m}$ (khoảng cách va chạm an toàn 5 mm).
  - `friction`: $0.5 - 0.8$ (ma sát giữ áo không bị tuột khỏi vai).
- **Self Collision trên Áo:** Bật self-collision với khoảng cách $0.003\text{ m}$ để các nếp gấp vải không tự xuyên vào nhau.

### 2.2. Kiểm soát Thời gian & Ổn định (Performance & Stability)
- Số frame mô phỏng: Giới hạn trong khoảng $30 - 60$ frames để vải kịp rơi và ổn định (settled state).
- Tối ưu thời gian: Thời gian chạy mô phỏng trên 1 mẫu phải <= 3 - 5 phút trên máy thông thường.
- Cơ chế Timeout: Script CLI phải có bộ đếm thời gian (ví dụ: tối đa 6 phút). Nếu quá hạn, ngắt tiến trình sạch sẽ và trả về mã lỗi `SIMULATION_TIMEOUT`, tuyệt đối không để treo tiến trình gây nghẽn tài nguyên.

---

## 3. Xử lý Trường hợp Ngoại lệ (Edge Cases)
1. **Áo bị rơi tự do xuống đất:** Do khoảng cách vai áo quá rộng so với cơ thể hoặc ma sát va chạm quá nhỏ. Khắc phục bằng cách gán nhóm đỉnh cố định tạm thời (Pinning group) ở phần cổ áo trong vài frame đầu hoặc tăng friction.
2. **Đỉnh áo bị xuyên thấu vĩnh viễn (Mesh Penetration Explosion):** Do body mesh có góc nhọn hoặc mặt hở. Khắc phục bằng cách tự động áp dụng Smooth Shading hoặc tăng Sub-frame steps trong solver.
3. **Lỗi `NaN` tọa độ đỉnh:** Bắt buộc kiểm tra tọa độ sau khi xuất mesh: nếu có bất kỳ đỉnh nào có tọa độ `NaN` hoặc `Inf`, hủy file xuất và báo lỗi `CORRUPTED_MESH`.

---

## 4. Tài liệu Tham khảo Chuyên sâu (References)
Khi giải quyết các vấn đề kỹ thuật cụ thể, hãy tra cứu các tài liệu trong `references/`:
- [blender-simulation-config.md](references/blender-simulation-config.md): Tham số chi tiết Cloth physics và lệnh CLI Blender headless.
- [size-chart-specs.md](references/size-chart-specs.md): Bảng thông số kích thước S/M/L/XL và nguyên tắc co dãn mesh.
- [edge-cases.md](references/edge-cases.md): Cẩm nang xử lý áo bị rơi, nổ mesh, hoặc timeout mô phỏng.
