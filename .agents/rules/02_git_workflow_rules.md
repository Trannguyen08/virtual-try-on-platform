# RULE 02: GIT WORKFLOW & ASSET PROTECTION

## 1. Nguyên tắc Thực thi Git
- **Agent tuyệt đối không chạy lệnh Git.** Agent chỉ soạn sẵn câu lệnh chuẩn xác trong code block để **User tự chạy**.
- Mọi thay đổi của Module M4 được thực hiện trên nhánh tính năng: `feature/fit-ai`.
- **CẤM** commit thẳng vào `main` hoặc `develop`.
- **CẤM TUYỆT ĐỐI** dùng `git push --force` hoặc các lệnh phá hủy lịch sử commit.

---

## 2. Bảo vệ Tài nguyên & Dữ liệu Lớn (Strict Asset Protection)
Dự án Virtual Try-On xử lý dữ liệu 3D và AI dung lượng rất lớn. Việc commit nhầm file lớn sẽ làm sập repo Git.

### 2.1. Danh sách CẤM COMMIT lên Git
Tuyệt đối không được add hay commit các định dạng sau:
1. **Model weights / Checkpoints:** `*.pt`, `*.pth`, `*.bin`, `*.onnx`, `*.safetensors`, `*.pkl`, `*.joblib`.
2. **Dữ liệu lớn / Mảng số học:** `*.npy`, `*.npz`, `*.parquet`, `*.h5`.
3. **Thư mục dữ liệu & cache:**
   - `ai/dataset/data/` (ảnh 30k, metadata lớn)
   - `tmp/` (toàn bộ file cache Hugging Face, parquet tạm)
   - `data/external/`, `data/raw/`, `data/synthetic/`, `data/outputs/`
4. **Môi trường ảo & IDE:** `.venv/`, `__pycache__/`, `.ipynb_checkpoints/`, `.vscode/`.

### 2.2. Kiểm tra Đồng bộ `.gitignore`
Trước khi đề xuất lệnh `git add .`, Agent và User phải đảm bảo `.gitignore` đã khai báo đầy đủ các đường dẫn cấm nói trên.

### 2.3. Lệnh Cứu nguy khi Lỡ Tracking File Lớn
Nếu lỡ chạy `git add` vào thư mục nặng, **KHÔNG ĐƯỢC XÓA FILE TRÊN Ổ ĐĨA**, mà dùng cờ `--cached` để chỉ gỡ tracking trong Git:
```powershell
# Gỡ tracking trong Git, giữ nguyên file thật trên ổ đĩa:
git rm -r --cached ai/dataset/data/
git rm -r --cached tmp/
git add .gitignore
git commit -m "chore(git): untrack large data and cache folders"
```

---

## 3. Quy chuẩn Đặt tên Commit (Conventional Commits)
Mỗi commit phải có tiền tố rõ ràng phản ánh đúng phạm vi thay đổi của M4:
- `feat(fit): ...` : Thêm tính năng đo đạc hình học, region fit, heatmap.
- `feat(ai): ...`  : Thêm pipeline dataset, train model, size recommender.
- `test(fit): ...` : Thêm hoặc cập nhật unit test cho module fit.
- `test(ai): ...`  : Thêm hoặc cập nhật unit test cho module AI.
- `docs(testing): ...`: Cập nhật tài liệu testing, nhật ký ca kiểm thử.
- `chore(git): ...`: Cấu hình hệ thống, cập nhật .gitignore.

---

## 4. Đồng bộ Nhánh Định kỳ (Keep Up-To-Date)
Để tránh conflict lớn khi nộp đồ án, Agent cần định kỳ nhắc nhở và đề xuất lệnh để User kéo cập nhật mới nhất từ `develop` về `feature/fit-ai`:
```powershell
git fetch origin
git merge origin/develop
```
