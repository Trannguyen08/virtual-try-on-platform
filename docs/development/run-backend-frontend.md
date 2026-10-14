# Chạy backend và frontend trên Windows

Chạy các lệnh dưới đây bằng PowerShell. Cần Python 3.10+ và Node.js/npm. Mở **hai cửa sổ terminal**, đều bắt đầu tại thư mục gốc của repo (`virtual-try-on-platform`).

## Terminal 1: backend

Lần đầu, tạo môi trường Python và cài dependency:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
```

Nếu đã có `.venv` và dependency đã được cài, bỏ qua hai lệnh trên. Tạo `.env` từ `.env.example` nếu chưa có, rồi đặt `BLENDER_PATH=D:/Blender/blender.exe` trong `.env` trên máy này. Khởi động FastAPI:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --env-file .env --reload --host 127.0.0.1 --port 8000
```

`--env-file .env` nạp cấu hình từ file trong thư mục gốc repo vào tiến trình backend. Sau khi sửa `.env`, dừng và khởi động lại Uvicorn; nếu terminal cũ đã đặt `$env:BLENDER_PATH`, hãy dùng terminal mới để giá trị trong file được áp dụng. Chỉ mở Blender GUI không làm backend đọc được đường dẫn. Nếu để trống `BLENDER_PATH`, backend thử `PATH`, `C:\Blender`, `D:\Blender`, `E:\Blender` và thư mục Blender Foundation trong Program Files. Blender cần cài và bật MPFB2 trong đúng phiên bản được chọn. Nếu thiếu MPFB2, job tạo body báo lỗi thay vì trả mannequin.

Kiểm tra tại [http://localhost:8000/health](http://localhost:8000/health) hoặc mở [Swagger UI](http://localhost:8000/docs). Có thể kiểm tra bằng lệnh:

```powershell
curl.exe http://localhost:8000/health
```

## Terminal 2: frontend

Lần đầu, cài dependency từ lockfile:

```powershell
cd frontend
npm.cmd ci
```

Nếu đã có `frontend/node_modules` phù hợp với lockfile, chỉ cần chuyển vào thư mục `frontend`. Khởi động Vite:

```powershell
npm.cmd run dev
```

Mở địa chỉ Vite in ra terminal, thông thường là [http://localhost:5173](http://localhost:5173). Giữ cả hai terminal đang chạy để dùng frontend với backend. Nhấn `Ctrl+C` trong từng terminal để dừng.

Frontend hiện gọi API tại `http://localhost:8000`; backend mặc định cho phép CORS từ `http://localhost:5173`. Nếu cổng 5173 đã bị chiếm và Vite tự chọn cổng khác, cần giải phóng cổng 5173 hoặc cấu hình lại `CORS_ORIGINS` cho backend trước khi chạy. Trong giao diện, cả nút tạo body từ thông số và nút tiếp tục với body mẫu đều gọi Blender MPFB2; ảnh chọn ở bước đầu chỉ là ảnh xem trước.
