# CI/CD PIPELINE DOCUMENTATION
**Dự án:** Virtual Try-On Platform  
**Workflow File:** `.github/workflows/ci.yml`

---

## 1. SƠ ĐỒ LUỒNG CI (PULL REQUEST WORKFLOW)

```
Push / Pull Request (vào dev / main)
   │
   ├──► [Job 1: Python Backend & AI]
   │       ├── Checkout repo
   │       ├── Setup Python 3.10 + Cache pip
   │       ├── Install backend/requirements-dev.txt (backend nhẹ + test/lint)
   │       ├── Lint Python (ruff check --select=E9,F63,F7,F82)
   │       └── Run Unit + Mock E2E (python -m pytest tests/unit/ tests/e2e/mock/ -m "not slow and not gpu")
   │
   └──► [Job 2: Frontend Web & 3D Viewer]
           ├── Checkout repo
           ├── Setup Node.js 20 + Cache npm
           ├── Install dependencies (npm install)
           └── Build check (npm run build)
```

---

## 2. QUY ĐỊNH BẢO VỆ NHÁNH (BRANCH PROTECTION)
- Nhánh tích hợp là `dev`; nhánh phát hành là `main`.
- Đề xuất bảo vệ hai nhánh bằng required checks cho Python và Frontend. Workflow
  tự nó không thiết lập branch protection; cần cấu hình trên GitHub. Lượt triển
  khai M3 này không push, tạo PR, merge hoặc thay đổi repository settings.

---

## 3. LƯU Ý VỀ TÀI NGUYÊN TRÊN CI
- **Không chạy Blender Headless nặng trên CI:** Các bài test mô phỏng vải chạy ở máy local và lưu evidence.
- **Không commit weights SMPL-X lên Git / CI:** Các bài test trên CI sử dụng dữ liệu giả lập (Mock mesh / Analytical geometry).
- **Job backend độc lập với frontend:** chỉ cài `backend/requirements-dev.txt`,
  không cài PyTorch/Open3D/MediaPipe. Khi module khác bổ sung test cần dependency
  nặng, cần tách job/marker phù hợp; không âm thầm bỏ kiểm thử backend mock.

## 4. KẾT QUẢ KIỂM TRA LOCAL

- Backend: 51 test unit/API + mock E2E pass trên Windows/Python 3.10.11.
  `pytest.ini` đã sửa sang cú pháp INI thật để pytest discover đúng test.
- Frontend: đã bổ sung `frontend/tsconfig.json`, `frontend/index.html` và
  `frontend/src/main.tsx`. `npm run build` chạy `tsc && vite build` thành công
  trên Windows/Node 22.22.2 (CI dùng Node 20), kiểm tra toàn bộ `src` và tạo
  `dist/index.html` cùng JavaScript bundle. Không tắt/skip bước kiểm tra nào.
- Entry React dùng `UploadPage` placeholder có sẵn; đây là scaffold build được,
  chưa phải giao diện try-on hoàn chỉnh. API envelope type khớp contract M3.
- GitHub Actions chưa chạy ở lượt này vì chưa push/PR; không tuyên bố toàn CI xanh.
- [Lệnh, kết quả và giới hạn kiểm thử](../report/evidence/backend/mock-api-validation.md).
