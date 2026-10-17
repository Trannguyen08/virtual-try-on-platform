# AGENT DIRECTIVE — VIRTUAL TRY-ON PLATFORM (DYNAMIC ROLE ROUTER)

## 1. Nguyên tắc Khởi động Nền tảng (Mandatory Common Rules)
Dù bạn đang hoạt động ở bất kỳ vai trò hay phân hệ nào trong dự án, bạn **BẮT BUỘC** phải tuân thủ 5 quy tắc nền tảng chung được định nghĩa trong `.agents/rules/common/`:

1. [01_agent_behavior.md](.agents/rules/common/01_agent_behavior.md) — Giới hạn quyền hạn (chỉ Đọc/Ghi file, không tự chạy lệnh terminal/git), chu trình thảo luận trước khi code.
2. [02_git_workflow.md](.agents/rules/common/02_git_workflow.md) — Quy chuẩn Git, làm việc trên feature branch, bảo vệ tài nguyên nặng (> 50MB, model weights, cache).
3. [03_testing_and_qa.md](.agents/rules/common/03_testing_and_qa.md) — Quy chuẩn viết test, gắn mã ID truy vết (`TC-xxx`), `pytest.approx`, cố định random seed và cơ chế Zero-Crash Fallback.
4. [04_contract_and_units.md](.agents/rules/common/04_contract_and_units.md) — Nguyên tắc Contract First, chuẩn hóa Đơn vị (**Mét** nội bộ, **Centimet** ngoại vi) và Hệ trục tọa độ (**Y-up, +Z forward**), cấm Silent Fix.
5. [05_change_impact_log.md](.agents/rules/common/05_change_impact_log.md) — Bắt buộc tạo Change Impact Log sau mỗi đợt sửa đổi code/config/contract trước khi báo hoàn thành.

---

## 2. Cơ chế Định tuyến Vai trò Động (Dynamic Role Activation)
Dự án Virtual Try-On Platform được cấu trúc thành 5 Module chuyên biệt. Agent **tự động xác định vai trò hiện tại** theo thứ tự ưu tiên sau:
1. **Theo yêu cầu trực tiếp của User:** Người dùng chỉ định module cần làm việc (ví dụ: *"chuyển sang làm M2"*, *"viết API backend"*, *"tối ưu Three.js"*).
2. **Theo nhánh Git hiện tại:** 
   - `feature/body` hoặc `feature/smplx-body` → **Role M1**
   - `feature/clothes` hoặc `feature/garment` → **Role M2**
   - `feature/backend` hoặc `feature/api` → **Role M3**
   - `feature/fit-ai` → **Role M4**
   - `feature/frontend` hoặc `feature/ui` → **Role M5**
3. **Theo phạm vi thư mục file đang thao tác:**
   - `body/**` → **Role M1**
   - `garment/**` → **Role M2**
   - `backend/**`, `shared/**` → **Role M3**
   - `fit/**`, `ai/**` → **Role M4**
   - `frontend/**` → **Role M5**

---

## 3. Bản đồ Quy tắc & Kỹ năng theo từng Role (Role-Specific Loading)
> [!IMPORTANT]
> **TIẾT KIỆM TOKEN & TẬP TRUNG NGỮ CẢNH:** Khi đã kích hoạt một Role, Agent **CHỈ ĐƯỢC PHÉP ĐỌC VÀ NẠP DUY NHẤT** file Rule và Skill tương ứng của Role đó. **TUYỆT ĐỐI KHÔNG NẠP CHÉO** các rule/skill của các module khác.

| Role | Tên Module & Chuyên môn | File Quy tắc Riêng (Role Rule) | Skill Chuyên sâu (Role Skill) |
| :---: | :--- | :--- | :--- |
| **M1** | **Body & Measurements**<br>Thị giác máy tính, MediaPipe 33 keypoints, mô hình SMPL-X 3D, cắt lớp mesh trích xuất 5 số đo. | [.agents/rules/roles/role_m1_body.md](.agents/rules/roles/role_m1_body.md) | [.agents/skills/m1-body-expert/SKILL.md](.agents/skills/m1-body-expert/SKILL.md) |
| **M2** | **Garment & Simulation**<br>3D Garment templates, hệ thống Size Chart S/M/L/XL, mô phỏng vật lý vải Blender bpy headless. | [.agents/rules/roles/role_m2_garment.md](.agents/rules/roles/role_m2_garment.md) | [.agents/skills/m2-garment-expert/SKILL.md](.agents/skills/m2-garment-expert/SKILL.md) |
| **M3** | **Backend, API & Integration**<br>FastAPI REST endpoints, quản lý Job bất đồng bộ, bộ điều phối Orchestrator linh hoạt Mock/Real. | [.agents/rules/roles/role_m3_backend.md](.agents/rules/roles/role_m3_backend.md) | [.agents/skills/m3-backend-expert/SKILL.md](.agents/skills/m3-backend-expert/SKILL.md) |
| **M4** | **Fit Metrics, Dataset & AI Models**<br>Chỉ số Penetration/Distance/Coverage, Fit Score giải tích, 15 đặc trưng nhân trắc học, AI Random Forest. | [.agents/rules/roles/role_m4_fit_ai.md](.agents/rules/roles/role_m4_fit_ai.md) | [.agents/skills/m4-fit-ai-expert/SKILL.md](.agents/skills/m4-fit-ai-expert/SKILL.md) |
| **M5** | **Frontend & 3D WebGL**<br>Three.js 3D Viewer tương tác xoay/zoom, Shader Vertex Colors hiển thị Fit Heatmap, giao diện người dùng. | [.agents/rules/roles/role_m5_frontend.md](.agents/rules/roles/role_m5_frontend.md) | [.agents/skills/m5-frontend-expert/SKILL.md](.agents/skills/m5-frontend-expert/SKILL.md) |
