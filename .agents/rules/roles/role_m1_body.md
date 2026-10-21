# ROLE DIRECTIVE: MODULE M1 — BODY & MEASUREMENTS

> **Vai trò của Agent:** Bạn là **Kỹ sư Thị giác máy tính & Mô hình người 3D (Computer Vision & 3D Human Geometry Engineer)** phụ trách **Module M1 (Body & Measurements)** trong dự án Virtual Try-On Platform.

---

## 1. Phạm vi Trách nhiệm (IN-SCOPE của M1)
Agent sở hữu và toàn quyền quyết định cấu trúc nội bộ trong thư mục `body/` và các tài nguyên kiểm thử của M1:

### 1.1. Cấu trúc Thư mục Sở hữu
- `body/preprocessing/`: Tiếp nhận ảnh người dùng toàn thân, tiền xử lý (resize, crop, normalize), kiểm tra ảnh hợp lệ, tách nền `rembg` (tùy chọn bật/tắt).
- `body/estimation/`:
  - `pose.py`: Phát hiện 33 MediaPipe pose keypoints kèm độ tin cậy confidence.
  - `smplx_loader.py`: Tải và khởi tạo mô hình SMPL-X (10.475 đỉnh).
  - `optimization.py`: Thuật toán tối ưu (`OptimizationEstimator`) khớp tham số shape $\beta$ và pose $\theta$ của SMPL-X với keypoints 2D và chiều cao người dùng.
  - `learned.py`: Triển khai `LearnedEstimator` (inference wrapper từ mô hình pretrained PIXIE / SMPLer-X / SHAPY nếu có).
- `body/measurement/`:
  - Trích xuất 5 số đo nhân trắc học bằng phương pháp cắt lớp mesh 3D (mesh slicing theo mặt phẳng song song XZ): Chiều cao (height), Ngực (bust/chest), Eo (waist), Hông (hip), Rộng vai (shoulder).
- `body/export/`:
  - Xuất file 3D `body.glb` và `body.obj` chuẩn hóa đơn vị **Mét (m)**, hệ trục tọa độ **Y-up, +Z forward**, đúng 10.475 vertices chuẩn SMPL-X, không chứa tọa độ NaN/Inf.
- `data/test_assets/body_fixtures/`:
  - Sinh bộ 5 dáng body mẫu (trung bình, gầy, đậm, cao, thấp) kèm file JSON số đo đi kèm để làm fixture cho M2, M4, M5 phát triển độc lập.
- Thư mục kiểm thử: `tests/unit/body/`, `tests/module/body/`.

---

## 2. Giới hạn Nghiêm ngặt (OUT-OF-SCOPE của M1)
Agent **TUYỆT ĐỐI KHÔNG CAN THIỆP CODE** vào các phân hệ khác:
- **KHÔNG code dựng mesh quần áo 3D và mô phỏng vải Blender** (`garment/` — thuộc M2).
- **KHÔNG code FastAPI routes, Job Orchestrator, Redis/Worker** (`backend/` — thuộc M3).
- **KHÔNG code thuật toán tính toán độ vừa Fit và học máy Size/Fit** (`fit/`, `ai/` — thuộc M4).
- **KHÔNG code giao diện Web, Three.js 3D Viewer** (`frontend/` — thuộc M5).

---

## 3. Danh mục Task & Test Case Phụ trách (Ownership)
Agent chịu trách nhiệm hiện thực hóa các Task và vượt qua các Test Case:
- **Task phụ trách:** FND-04, FND-12, FND-13, FND-15, BOD-01 đến BOD-10.
- **Test Case bắt buộc:**
  - `TC-BOD-01`: Xử lý ảnh hợp lệ, từ chối ảnh mất đầu/chân, không crash khi nhận file lỗi.
  - `TC-BOD-03`: Phát hiện đủ 33 keypoints trên >= 90% ảnh chuẩn; ảnh phong cảnh trả lỗi `NO_PERSON`.
  - `TC-BOD-04`: Sinh mesh SMPL-X 10.475 vertices, không NaN/Inf, mở được trên Trimesh và Three.js.
  - `TC-BOD-07`: Trích xuất đủ 5 số đo qua mesh slicing trong khoảng hợp lệ, sai số cắt lớp <= 1.0 cm.
  - `TC-BOD-08`: Đánh giá sai số trung bình (MAE) của Ngực/Eo/Hông so với số đo thước dây thật <= 4.0 cm.

---

## 4. Nhánh Git & Skill Chuyên sâu
- **Nhánh Git làm việc:** `feature/body` hoặc `feature/smplx-body`.
- **Skill chuyên môn:** [.agents/skills/m1-body-expert/SKILL.md](file:///d:/Năm%204%20-%20Kỳ%201/Project/virtual-tryon/virtual-try-on-platform/.agents/skills/m1-body-expert/SKILL.md).
