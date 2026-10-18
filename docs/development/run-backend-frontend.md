# Chạy backend và frontend trên Windows

Chạy các lệnh dưới đây bằng PowerShell. Cần Python 3.10+ và Node.js/npm. Mở **hai cửa sổ terminal**; các terminal bắt đầu tại thư mục gốc của repo (`virtual-try-on-platform`). Backend chính cũng phục vụ tính năng tạo trang phục 3D trên cổng 8000.

## Terminal 1: backend

Lần đầu, tạo môi trường Python và cài dependency:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
```

Backend chính dùng PostgreSQL cho metadata body, asset, job và bước xử lý. Khởi động PostgreSQL trước, tạo database `tryon` và đặt `DATABASE_URL` trong `.env` (xem `.env.example`). Có thể dùng `docker compose up -d postgres` cho database phát triển. Sau khi cài dependency, chạy migration **trước** khi khởi động API:

Nếu chỉ cần database và pgAdmin, không cần chạy backend/frontend:

```powershell
docker compose up -d postgres pgadmin
docker compose ps postgres pgadmin
```

Compose dùng image `postgres:16-alpine` và `dpage/pgadmin4:latest` có sẵn, lưu dữ liệu trong hai named volume riêng. PostgreSQL ở `127.0.0.1:5432`, database/user/password phát triển là `tryon`/`tryon`/`tryon`. Mở pgAdmin tại `http://127.0.0.1:5050`, đăng nhập bằng `PGADMIN_DEFAULT_EMAIL` và `PGADMIN_DEFAULT_PASSWORD` trong `.env` (giá trị mẫu trong `.env.example`). Khi thêm server trong pgAdmin, dùng host **`postgres`**, port `5432`, database `tryon`, username/password `tryon`/`tryon`; không dùng `localhost` vì pgAdmin chạy trong container khác. Lệnh trên chỉ chọn `postgres` và `pgadmin`, không build hay khởi động backend/frontend.

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Với `docker compose up --build`, service backend chờ PostgreSQL healthy và tự chạy `alembic upgrade head` trước Uvicorn. Dữ liệu PostgreSQL nằm trong named volume `postgres_data`; file asset tạo trong `data/assets/` cần được giữ cùng database khi backup hoặc chuyển máy. Không đưa mật khẩu thật vào `.env.example` hay commit `.env`.

Nếu đã có `.venv`, cài lại dependency sau khi cập nhật repo để có OpenCV, Trimesh và các gói Garment 3D. Tạo `.env` từ `.env.example` nếu chưa có, rồi đặt `BLENDER_PATH=D:/Blender/blender.exe` trong `.env` trên máy này. `GARMENT3D_PROVIDER=local` là mặc định; có thể ghi rõ trong `.env`. Khởi động FastAPI:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --env-file .env --reload --host 127.0.0.1 --port 8000
```

`--env-file .env` nạp cấu hình từ file trong thư mục gốc repo vào tiến trình backend. Sau khi sửa `.env`, dừng và khởi động lại Uvicorn; nếu terminal cũ đã đặt `$env:BLENDER_PATH`, hãy dùng terminal mới để giá trị trong file được áp dụng. Chỉ mở Blender GUI không làm backend đọc được đường dẫn. Nếu để trống `BLENDER_PATH`, backend thử `PATH`, `C:\Blender`, `D:\Blender`, `E:\Blender` và thư mục Blender Foundation trong Program Files. Blender cần cài và bật MPFB2 trong đúng phiên bản được chọn. Nếu thiếu MPFB2, job tạo body báo lỗi thay vì trả mannequin.

Kiểm tra tại [http://localhost:8000/health](http://localhost:8000/health) và [http://localhost:8000/garment3d/health](http://localhost:8000/garment3d/health), hoặc mở [Swagger UI của backend chính](http://localhost:8000/docs) và [Swagger UI của Garment 3D](http://localhost:8000/garment3d/docs). Có thể kiểm tra bằng lệnh:

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

Mở địa chỉ Vite in ra terminal, thông thường là [http://localhost:5173](http://localhost:5173). Giữ các terminal của dịch vụ đang dùng mở trong lúc thử giao diện. Nhấn `Ctrl+C` trong từng terminal để dừng.

## Tạo trang phục 3D từ ảnh

Mở [http://localhost:5173/garment-3d](http://localhost:5173/garment-3d) hoặc chọn mục **Tạo trang phục 3D** trong menu. Frontend gọi các route `/garment3d/...` trên backend chính tại `http://localhost:8000`; không cần tiến trình backend thứ hai. Nếu API chạy ở origin khác, đặt `VITE_API_URL` cho frontend trước khi chạy Vite. Đường dẫn cũ `/garment3d.html` chuyển tiếp đến trang mới. Xem thêm [hướng dẫn Garment 3D](../../frontend/GARMENT3D.md).

Frontend hiện gọi API tại `http://localhost:8000`; backend mặc định cho phép CORS từ `http://localhost:5173`. Nếu cổng 5173 đã bị chiếm và Vite tự chọn cổng khác, cần giải phóng cổng 5173 hoặc cấu hình lại `CORS_ORIGINS` cho backend trước khi chạy. Trong giao diện, cả nút tạo body từ thông số và nút tiếp tục với body mẫu đều gọi Blender MPFB2; ảnh chọn ở bước đầu chỉ là ảnh xem trước.

Xem [kế hoạch ghép body với trang phục 3D đã tạo](body-garment-tryon-integration-plan.md) để biết các đầu việc, thứ tự triển khai và tiêu chí nghiệm thu cho luồng thử đồ thật.

### Giới hạn hiện tại của lưu trữ

`/api/tryon/analyze` lưu metadata body mock; `/api/tryon/fit` lưu job, kết quả/lỗi và thời gian xử lý vào PostgreSQL. Các GLB mock được đăng ký trong bảng asset khi API khởi động và vẫn truy cập được sau restart nếu file còn trên disk. Repository/service có thể đăng ký body MPFB và các loại asset (`original_image`, `foreground_image`, `mesh`, `texture`, `glb`) khi pipeline thật bàn giao file. Ảnh upload của `/api/tryon/analyze` hiện **không** được lưu. `/api/body-builder` vẫn dùng job trong bộ nhớ và `/garment3d` vẫn dùng SQLite riêng; việc hợp nhất hai luồng này cần triển khai tiếp. `BackgroundTasks` chưa phải queue bền vững: job đang chạy khi API dừng có thể giữ trạng thái `running` và cần cơ chế recovery/worker sau này.
