---
name: m5-frontend-expert
description: Chuyên môn kỹ thuật về Three.js 3D WebGL Viewer, Custom Heatmap Shaders và Xây dựng Giao diện Người dùng Thử đồ Ảo cho Module M5 trong Virtual Try-On Platform.
---

# M5 FRONTEND & 3D WEBGL EXPERT SKILL

## 1. Bản chất Kiến trúc M5 (Interactive 3D Dressing Room)
Module M5 là mặt tiền trải nghiệm của người dùng (User Experience), nơi kết hợp giao diện web hiện đại với khung nhìn 3D WebGL trực quan:

```text
┌────────────────────────────────────────────────────────┐
│               GIAO DIỆN PHÒNG THỬ ĐỒ ẢO               │
├──────────────────────────┬─────────────────────────────┤
│   3D WEBGL VIEWER        │       BẢNG ĐIỀU KHIỂN       │
│   (Three.js Scene)       │       (Fit Panel & Options) │
│                          │                             │
│  - Load body.glb         │  - Form tải ảnh / số đo     │
│  - Load draped.glb       │  - Điểm Fit Score [0, 100]  │
│  - OrbitControls 360°    │  - Nhãn Too Tight/Good/Loose│
│  - Vertex Color Heatmap  │  - Size khuyến nghị bởi AI  │
│  - Nút Bật/Tắt Heatmap   │  - Bộ chọn size (S/M/L/XL)  │
│                          │                             │
└──────────────────────────┴─────────────────────────────┘
```

---

## 2. Phương pháp luận Kỹ thuật Cốt lõi

### 2.1. Cấu hình Three.js Scene Chuẩn
- **Camera:** Sử dụng `PerspectiveCamera` (FOV $45^\circ$, near $0.1$, far $1000$). Vị trí camera hướng vào tâm thân người ($y \approx 0.9\text{ m}$), khoảng cách $z \approx 2.2\text{ m}$.
- **Hệ thống Ánh sáng (Lighting):**
  - `AmbientLight` (cường độ $0.6$) tạo ánh sáng nền mềm mại.
  - 2 `DirectionalLight` (ánh sáng chính phía trước góc $45^\circ$ và ánh sáng phụ ngược sáng rim-light phía sau) để thấy rõ độ nổi khối của vải.
- **Tải và Đồng bộ Mesh:** Dùng `GLTFLoader` tải cả `body.glb` và `draped.glb`. Bắt buộc kiểm tra tỉ lệ và giữ nguyên gốc tọa độ $(0, 0, 0)$ để áo khớp hoàn hảo quanh cơ thể.

### 2.2. Kỹ thuật Tô màu Fit Heatmap (Vertex Color Shader)
- Không dùng texture ảnh tĩnh. Áp dụng kỹ thuật tô màu trực tiếp trên từng đỉnh (Vertex Colors):
  - Đọc mảng khoảng cách từ file `heatmap.json` (độ dài đúng bằng số đỉnh của mesh áo).
  - Chuẩn hóa khoảng cách sang dải màu:
    - Khoảng cách âm hoặc $< 0.005\text{ m}$ (Chật/Căng): Màu **Đỏ** (`rgb(239, 68, 68)`).
    - Khoảng cách lý tưởng $0.015 - 0.035\text{ m}$ (Vừa vặn): Màu **Xanh lá** (`rgb(34, 197, 94)`).
    - Khoảng cách $> 0.05\text{ m}$ (Rộng/Thùng thình): Màu **Xanh dương** (`rgb(59, 130, 246)`) hoặc Vàng.
  - Gán vào thuộc tính `geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3))` và kích hoạt `material.vertexColors = true`.

---

## 3. Xử lý Trường hợp Ngoại lệ (Edge Cases)
1. **API Backend phản hồi chậm hoặc lỗi 500:** Tuyệt đối không để vỡ giao diện (màn hình trắng). Hiển thị Toast thông báo lỗi thân thiện hoặc bật Fallback Mock Data để người dùng vẫn trải nghiệm được giao diện.
2. **File Mesh quá nặng làm tụt FPS:** Tự động phát hiện FPS $< 20$ để giảm cấp độ khử răng cưa (antialiasing) hoặc hạ độ phân giải pixel ratio trên thiết bị yếu.
3. **Mô phỏng đang chạy nền (Async Polling):** Khi người dùng đổi size, hiển thị trạng thái loading spinner mượt mà trên avatar, tự động polling trạng thái job mỗi $2 - 3$ giây và có nút hủy nếu người dùng không muốn chờ.

---

## 4. Tài liệu Tham khảo Chuyên sâu (References)
Khi giải quyết các vấn đề kỹ thuật cụ thể, hãy tra cứu các tài liệu trong `references/`:
- [threejs-viewer-setup.md](references/threejs-viewer-setup.md): Cấu hình Scene, Camera framing, Lighting và OrbitControls.
- [heatmap-colormap.md](references/heatmap-colormap.md): Thang màu Heatmap và kỹ thuật tô màu Vertex Colors.
- [ux-flows-and-states.md](references/ux-flows-and-states.md): Luồng tương tác người dùng và quản lý trạng thái Client.
