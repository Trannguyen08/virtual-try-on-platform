# RULE 02: GIT WORKFLOW & ASSET PROTECTION (COMMON)

> **Phạm vi áp dụng:** Áp dụng bắt buộc cho toàn bộ Agent ở mọi Role (M1, M2, M3, M4, M5).

---

## 1. Nguyên tắc Thực thi Git
- **Agent tuyệt đối không chạy lệnh Git.** Agent chỉ soạn sẵn câu lệnh chuẩn xác trong code block để **User tự chạy**.
- Mọi thay đổi phải được thực hiện trên nhánh tính năng (feature branch) tương ứng với từng module:
  - Module M1: `feature/body` hoặc `feature/smplx-body`
  - Module M2: `feature/clothes` hoặc `feature/garment`
  - Module M3: `feature/backend`
  - Module M4: `feature/fit-ai`
  - Module M5: `feature/frontend`
- **CẤM** commit thẳng vào `main` hoặc `develop`.
- **CẤM TUYỆT ĐỐI** dùng `git push --force` hoặc các lệnh phá hủy lịch sử commit.

---

## 2. Bảo vệ Tài nguyên & Dữ liệu Lớn (Strict Asset Protection)
Dự án Virtual Try-On xử lý dữ liệu 3D, mô phỏng vải và mô hình AI dung lượng rất lớn. Việc commit nhầm file lớn sẽ làm sập repo Git.

### 2.1. Danh sách CẤM COMMIT lên Git
Tuyệt đối không được add hay commit các định dạng sau:
1. **Model weights / Checkpoints nặng (> 50MB):** `*.pt`, `*.pth`, `*.bin`, `*.onnx`, `*.safetensors`, file weights SMPL-X.
2. **Dữ liệu mảng số học & cache tạm:** `*.npy`, `*.npz`, `*.parquet`, `*.h5`.
3. **Thư mục dữ liệu & cache nội bộ:**
   - `ai/dataset/data/` (ảnh 30k, metadata lớn)
   - `tmp/` (toàn bộ file cache Hugging Face, parquet tạm)
   - `data/external/`, `data/raw/`, `data/synthetic/`, `data/outputs/`
4. **Môi trường ảo & IDE:** `.venv/`, `node_modules/`, `__pycache__/`, `.ipynb_checkpoints/`, `.vscode/`.

### 2.2. Kiểm tra Đồng bộ `.gitignore`
Trước khi đề xuất lệnh `git add .`, Agent và User phải đảm bảo `.gitignore` đã khai báo đầy đủ các đường dẫn cấm nói trên.

### 2.3. Lệnh Cứu nguy khi Lỡ Tracking File Lớn
Nếu lỡ chạy `git add` vào thư mục nặng, **KHÔNG ĐƯỢC XÓA FILE TRÊN Ổ ĐĨA**, mà dùng cờ `--cached` để chỉ gỡ tracking trong Git:
```powershell
# Gỡ tracking trong Git, giữ nguyên file thật trên ổ đĩa:
git rm -r --cached ai/dataset/data/
git rm -r --cached tmp/
git rm -r --cached data/
git add .gitignore
git commit -m "chore(git): untrack large data and cache folders"
```

---

## 3. Quy chuẩn Đặt tên Commit (Conventional Commits)
Mỗi commit phải có tiền tố rõ ràng phản ánh đúng phạm vi thay đổi:
- `feat(body): ...` cho Module M1
- `feat(garment): ...` hoặc `feat(sim): ...` cho Module M2
- `feat(backend): ...` hoặc `feat(api): ...` cho Module M3
- `feat(fit): ...` hoặc `feat(ai): ...` cho Module M4
- `feat(frontend): ...` hoặc `feat(viewer): ...` cho Module M5
- `fix(...)`, `test(...)`, `docs(...)`, `chore(...)`, `refactor(...)`
