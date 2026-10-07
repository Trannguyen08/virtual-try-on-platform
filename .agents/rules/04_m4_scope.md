# RULE 04: M4 SCOPE & MODULE BOUNDARIES

## 1. Phạm vi Trách nhiệm (IN-SCOPE của M4)
Module M4 đóng vai trò là "Bộ não tính toán & AI" (Core Intelligence) của dự án. M4 sở hữu và toàn quyền quyết định cấu trúc nội bộ trong các thư mục sau:

### 1.1. Thư mục `fit/` (Hình học & Đánh giá Độ vừa Vặn)
- `fit/metrics/`: Tính toán 3 chỉ số cơ bản: Xuyên thấu (Penetration), Khoảng cách (Distance), Bao phủ (Coverage).
- `fit/region/`: Phân chia đỉnh theo vùng cơ thể (*Chest, Waist, Shoulder, Hip*) và phân lớp độ vừa từng vùng (`TIGHT / GOOD / LOOSE`).
- `fit/score/`: Tính điểm tổng thể Fit Score theo công thức chuẩn hóa và phân loại toàn thân.
- `fit/heatmap/`: Xuất mảng khoảng cách trên từng đỉnh (`heatmap.json`) để phục vụ tô màu 3D trên WebGL.

### 1.2. Thư mục `ai/` (Học máy & Đề xuất Kích cỡ)
- `ai/dataset/`: Pipeline sinh dữ liệu synthetic (v1), xử lý đặc trưng, gán nhãn, và chia tập train/val/test có seed.
- `ai/models/`: Định nghĩa và đóng gói các model: Size Recommender (dự đoán size áo), Fit Predictor (dự đoán độ vừa vặn) kèm cơ chế Wrapper.
- `ai/training/`: Huấn luyện các mô hình học máy (Random Forest, XGBoost, MLP, v.v.).
- `ai/evaluation/`: Đánh giá hiệu năng mô hình, vẽ biểu đồ Confusion Matrix, đối chiếu kết quả AI với Geometry Baseline.

### 1.3. Thư mục Kiểm thử & Báo cáo thuộc M4
- `tests/unit/fit/`, `tests/unit/ai/`
- `tests/integration/INT-04/`, `tests/integration/INT-06/`, `tests/integration/INT-07/`
- `docs/testing/acceptance-criteria/acceptance-criteria-fit-ai.md`
- `docs/testing/test-cases/test-cases-fit-ai.md`
- `docs/report/evidence/fit/`, `docs/report/evidence/ai/`

---

## 2. Giới hạn Nghiêm ngặt (OUT-OF-SCOPE của M4)
M4 **TUYỆT ĐỐI KHÔNG TỰ Ý THỰC HIỆN HAY CAN THIỆP CODE** vào các phần việc thuộc thẩm quyền của Module khác:
- **KHÔNG code tái tạo cơ thể người 3D / SMPL-X** (Thuộc M1 — `body/`).
- **KHÔNG code dựng mesh quần áo 3D** (Thuộc M2 — `garment/mesh/`).
- **KHÔNG code mô phỏng vải Blender simulation / draping** (Thuộc M2 — `garment/simulation/`).
- **KHÔNG code FastAPI routes, Job Manager, Orchestrator, Server** (Thuộc M3 — `backend/`).
- **KHÔNG code Web UI, React components, Three.js 3D Viewer** (Thuộc M5 — `frontend/`).

---

## 3. Quyền hạn Tương tác & Nguyên tắc Độc lập (Decoupling)
Để không bị phụ thuộc vào tiến độ của M1, M2 hay M3, M4 được phép:
1. **Tạo dữ liệu Mock / Synthetic tự lập:**
   - Dùng các khối hình học cơ bản (khối cầu lồng nhau, hình trụ) để test thuật toán `fit/`.
   - Dùng hàm phân phối thống kê nhân trắc học để sinh số đo cơ thể cho `ai/`.
2. **Kiểm tra hợp đồng dữ liệu (Contract Validation):**
   - M4 có quyền kiểm tra xem dữ liệu do M1, M2 truyền vào có đúng Schema, đúng đơn vị (mét) và hệ trục tọa độ (Y-up) hay không.
3. **Báo cáo lỗi (No Silent Fix):**
   - Nếu phát hiện đầu ra của M1 hoặc M2 bị lỗi (ví dụ: mesh có đỉnh NaN, sai đơn vị cm thay vì m), M4 **BẮT BUỘC BÁO CÁO LỖI**, tuyệt đối không tự viết code vá ngầm lỗi của module khác.

---

## 4. Phạm vi Chỉnh sửa File Cho phép (Allowed Edit Scope)
Agent **CHỈ ĐƯỢC PHÉP TẠO VÀ SỬA ĐỔI FILE** nằm trong các đường dẫn sau:
- `fit/**`
- `ai/**`
- `tests/unit/fit/**`, `tests/unit/ai/**`
- `tests/integration/INT-04/**`, `tests/integration/INT-06/**`, `tests/integration/INT-07/**`
- `docs/testing/**`
- `docs/report/evidence/fit/**`, `docs/report/evidence/ai/**`
- `.agents/**`

*Nghiêm cấm mọi hành vi refactor hàng loạt, đổi cấu trúc project hoặc xóa file ngoài phạm vi trên.*
