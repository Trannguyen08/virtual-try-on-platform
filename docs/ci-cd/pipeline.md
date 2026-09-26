# CI/CD PIPELINE DOCUMENTATION
**Dự án:** Virtual Try-On Platform  
**Workflow File:** `.github/workflows/ci.yml`

---

## 1. SƠ ĐỒ LUỒNG CI (PULL REQUEST WORKFLOW)

```
Pull Request (mở vào develop / main)
   │
   ├──► [Job 1: Python Backend & AI]
   │       ├── Checkout repo
   │       ├── Setup Python 3.10 + Cache pip
   │       ├── Install dependencies (requirements.txt, ruff, pytest)
   │       ├── Lint Python (ruff check --select=E9,F63,F7,F82)
   │       └── Run Fast Unit Tests (pytest -m "not slow and not gpu")
   │
   └──► [Job 2: Frontend Web & 3D Viewer]
           ├── Checkout repo
           ├── Setup Node.js 20 + Cache npm
           ├── Install dependencies (npm install)
           └── Build check (npm run build)
```

---

## 2. QUY ĐỊNH BẢO VỆ NHÁNH (BRANCH PROTECTION)
- Mọi PR chỉ được phép merge vào `develop` hoặc `main` khi **cả 2 jobs (Python và Frontend) đều báo Xanh (PASS)**.
- Nếu có lỗi cú pháp, lỗi lint nghiêm trọng, hoặc bất kỳ Unit test nhanh nào bị FAIL $\rightarrow$ Hệ thống tự động khóa nút Merge.

---

## 3. LƯU Ý VỀ TÀI NGUYÊN TRÊN CI
- **Không chạy Blender Headless nặng trên CI:** Các bài test mô phỏng vải chạy ở máy local và lưu evidence.
- **Không commit weights SMPL-X lên Git / CI:** Các bài test trên CI sử dụng dữ liệu giả lập (Mock mesh / Analytical geometry).
