# CI OpenCV và Vercel frontend

- Vai trò: M4 điều phối thay đổi cấu hình dùng chung theo yêu cầu người dùng. Owner liên quan: M2 (phụ thuộc OpenCV của garment), M5 (deploy frontend), người quản trị CI/Vercel.
- Thời điểm: 2026-10-17 10:05 Asia/Saigon.
- Mục đích: bảo đảm job Python có OpenCV và cấu hình Vercel khớp khi Root Directory là `frontend`.

## File thay đổi

| File | Trước → sau | Mục liên quan |
| --- | --- | --- |
| `.github/workflows/ci.yml` | Bước Install dependencies chỉ cài `backend/requirements-dev.txt` → cài thêm `opencv-python-headless>=4.9.0` trước lint và test. | Job `backend-and-ai`, bước `Install dependencies`; phiên bản tối thiểu theo `backend/garment3d/requirements.txt`. |
| `frontend/vercel.json` | Chỉ có rewrite mọi route về `/index.html` → thêm `buildCommand: npm run build` và `outputDirectory: dist`, giữ rewrite. | Cấu hình build/deploy Vercel khi Root Directory là `frontend`. |

## Ảnh hưởng và phối hợp

- API, schema, đơn vị, database, asset: không đổi; hai file chỉ chứa cấu hình CI/deploy và không sửa contract dữ liệu.
- Module khác: CI Python cài thêm OpenCV cho code garment M2; frontend M5 build bằng script hiện có (`tsc && vite build`) và xuất `dist` theo mặc định Vite. Thay đổi chỉ áp dụng cho dự án Vercel chọn Root Directory là `frontend`.
- Xung đột xác nhận: `vercel.json` ở root đang dùng `cd frontend && npm install && npm run build` với output `frontend/dist`, khác đường dẫn tương đối của cấu hình trong `frontend/vercel.json`. Đây là hai trường hợp Root Directory khác nhau; file ở root không được sửa trong đợt này.
- Nguy cơ: nếu dự án Vercel thực tế chưa chọn Root Directory `frontend`, cấu hình trong `frontend/vercel.json` không được dùng. Người quản trị Vercel cần xác nhận thiết lập trên dashboard.

## Kiểm tra và bàn giao

- Test/build thực tế: chưa chạy; quy tắc repo yêu cầu người dùng tự chạy lệnh kiểm tra. Chưa có log CI hoặc deploy mới để xác nhận kết quả.
- Người nhận bàn giao: người quản trị CI kiểm tra job `backend-and-ai`; M5/người quản trị Vercel xác nhận Root Directory `frontend`, build `npm run build`, output `dist`, và kiểm tra route SPA sau deploy.
