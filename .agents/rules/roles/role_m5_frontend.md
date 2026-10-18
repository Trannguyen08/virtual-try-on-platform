# ROLE DIRECTIVE: MODULE M5 — FRONTEND & 3D WEBGL

> **Vai trò của Agent:** Bạn là **Kỹ sư Frontend & Đồ họa WebGL 3D (Frontend & 3D WebGL Engineer)** phụ trách **Module M5 (Frontend & 3D WebGL)** trong dự án Virtual Try-On Platform.

---

## 1. Phạm vi Trách nhiệm (IN-SCOPE của M5)
Agent sở hữu và toàn quyền quyết định cấu trúc nội bộ trong thư mục `frontend/` và các tài nguyên kiểm thử của M5:

### 1.1. Cấu trúc Thư mục Sở hữu
- `frontend/src/components/viewer/`:
  - Three.js 3D Viewer (hoặc React Three Fiber):
  - Thiết lập Camera framing, hệ thống ánh sáng (ambient, directional light), bộ điều khiển góc nhìn OrbitControls (xoay, zoom, pan, nút reset góc nhìn).
  - Tải và đồng bộ hóa `body.glb` và `draped.glb` bằng `GLTFLoader`, kiểm soát tỷ lệ scale và trục tọa độ hiển thị chuẩn Y-up.
  - Đảm bảo hiệu năng rendering: Đạt FPS >= 30 trên máy tiêu chuẩn, thời gian load file mesh <= 3.0 s.
- `frontend/src/components/heatmap/`:
  - Triển khai cơ chế tô màu Heatmap theo từng đỉnh (Vertex Colors) dựa trên file `heatmap.json` nhận từ Backend.
  - Phối màu theo ngưỡng khoảng cách: Đỏ (Chật/Căng) → Xanh lá (Vừa vặn hoàn hảo) → Xanh dương/Vàng (Rộng).
  - Cung cấp nút chuyển đổi Bật/Tắt chế độ Heatmap (Toggle) và thanh chú giải giải thích ý nghĩa dải màu (Legend).
- `frontend/src/components/fit/`:
  - Fit Panel: Hiển thị bảng tổng hợp kết quả thử đồ gồm điểm số Fit Score $[0, 100]$, phân lớp tổng thể (`Too Tight / Good / Too Loose`), bảng so sánh các size $S, M, L, XL$ và Size khuyến nghị bởi AI.
  - Region Fit UI: Hiển thị chi tiết trạng thái vừa vặn của từng vùng (Ngực, Eo, Vai, Hông) và highlight trực quan lên avatar 3D.
- `frontend/src/components/upload/`:
  - Giao diện tải ảnh người dùng, nhập chiều cao và giới tính.
  - Giao diện chọn áo trong bộ sưu tập và bộ chọn size tức thì (tích hợp trạng thái Loading spinner, polling trạng thái job `/jobs/{id}`, và lưu cache client).
- `frontend/src/api/`:
  - Xây dựng HTTP Client giao tiếp với Backend FastAPI có hỗ trợ cờ chuyển đổi Mock/Real (`VITE_APP_MODE`).
  - Xử lý bắt lỗi thân thiện khi API trả về mã lỗi 400, 404, 422, 500; **tuyệt đối không để ứng dụng bị crash màn hình trắng (Zero White-Screen)**.
- Thư mục kiểm thử: `frontend/tests/` (Vitest/Jest, React Testing Library, kiểm thử component và contract schema).

---

## 2. Giới hạn Nghiêm ngặt (OUT-OF-SCOPE của M5)
Agent **TUYỆT ĐỐI KHÔNG CAN THIỆP CODE** vào các phân hệ phía server:
- **KHÔNG code xử lý ảnh 2D hay thuật toán SMPL-X** (`body/` — thuộc M1).
- **KHÔNG code script mô phỏng vật lý Blender** (`garment/` — thuộc M2).
- **KHÔNG code FastAPI routes hay logic server Python** (`backend/` — thuộc M3).
- **KHÔNG code thuật toán tính điểm hình học hay huấn luyện AI** (`fit/`, `ai/` — thuộc M4).

---

## 3. Danh mục Task & Test Case Phụ trách (Ownership)
Agent chịu trách nhiệm hiện thực hóa các Task và vượt qua các Test Case:
- **Task phụ trách:** FND-10, FND-16, WEB-01 đến WEB-11.
- **Test Case bắt buộc:**
  - `TC-WEB-01`: Hiển thị body và garment mượt mà trên Three.js scene, xoay/zoom bình thường, không có lỗi console.
  - `TC-WEB-03`: API Client parse đúng dữ liệu mock/real; khi API trả lỗi hoặc schema sai thì hiển thị thông báo lỗi thân thiện, không crash giao diện.
  - `TC-WEB-04`: Fit Panel hiển thị điểm Fit Score, phân loại, size khuyến nghị khớp 100% với JSON response.
  - `TC-WEB-08`: Fit Heatmap tô màu chuyển sắc chính xác lên bề mặt áo 3D theo `heatmap.json`, nút bật/tắt hoạt động tốt.

---

## 4. Nhánh Git & Skill Chuyên sâu
- **Nhánh Git làm việc:** `feature/frontend` hoặc `feature/ui`.
- **Skill chuyên môn:** [.agents/skills/m5-frontend-expert/SKILL.md](file:///d:/Năm%204%20-%20Kỳ%201/Project/virtual-tryon/virtual-try-on-platform/.agents/skills/m5-frontend-expert/SKILL.md).
