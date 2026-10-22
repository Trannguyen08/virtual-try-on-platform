# Virtual Try-On Platform

Mục tiêu dự án: thử đồ 3D và gợi ý size. **Hiện đã có backend mock MVP**, chưa có
pipeline xử lý ảnh/AI thật hay frontend hoàn chỉnh. Số đo/nhãn fit và các GLB
hình khối là dữ liệu demo, luôn có `source: "mock"`; score/confidence là `null`.

Contract để M1/M2/M4/M5 tích hợp: [docs/api/api-contract.md](docs/api/api-contract.md).
Tổng quan và kiến trúc hệ thống: [docs/project-overview.md](docs/project-overview.md) | [docs/architecture/system-architecture.md](docs/architecture/system-architecture.md).

## Chạy backend trên Windows

Python 3.10+; chạy từ thư mục gốc repo. Các lệnh dưới dùng được trong **CMD và
PowerShell**, không cần activate venv. Nếu `.venv` đã tồn tại, bỏ qua lệnh tạo. Sao chép `.env.example` thành `.env` nếu chưa có và chỉnh `BLENDER_PATH` trong `.env`.

```text
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --env-file .env --reload --host 127.0.0.1 --port 8000
```

Mở [Swagger UI](http://localhost:8000/docs) hoặc
[OpenAPI JSON](http://localhost:8000/openapi.json). Backend chỉ cần dependency
nhẹ ở `backend/requirements*.txt`; `requirements.txt` tại root còn bao gồm
thư viện AI/3D cho các module tương lai, không cần cài để chạy mock.

Chỉ dùng **một worker**. Body/job lưu trong bộ nhớ; restart/reload làm mất ID.
Không DB, queue bền vững, xác thực, mô phỏng vải hoặc inference AI.

CORS mặc định cho `http://localhost:5173`, `http://127.0.0.1:5173` (Vite),
và hai địa chỉ tương ứng cổng 3000 (Docker frontend). Nếu cần đổi, đặt biến
môi trường trước khi chạy server:

```bat
REM Chỉ CMD
set CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

```powershell
# Chỉ PowerShell
$env:CORS_ORIGINS = 'http://localhost:5173,http://127.0.0.1:5173'
```

Backend đọc `.env` khi khởi động bằng tùy chọn `--env-file .env`; sửa file này cần khởi động lại Uvicorn.

## Tạo body 3D bằng Blender trong giao diện hiện tại

Luồng thử đồ dùng Blender MPFB2 để xuất GLB cho cả body mặc định và body chỉnh từ thông số. Người dùng chỉnh chiều cao, cân nặng, tuổi, giới tính, màu da và tỷ lệ; chọn sản phẩm. Viewer trong giao diện hiện tại cho xem body hoặc body có trang phục minh họa, xoay/zoom, đổi màu, xem khung lưới và tải GLB. Ảnh ở bước đầu chỉ được xem trước, chưa dùng để suy hình dáng hoặc số đo.

Cài Blender 4.x hoặc 5.x và đặt đường dẫn trong `.env`:

```dotenv
BLENDER_PATH=D:/Blender/blender.exe
```

Đường dẫn trên là vị trí Blender đã xác nhận trên máy này; thay bằng vị trí Blender của bạn nếu khác. Lệnh chạy backend ở trên dùng `--env-file .env` để nạp giá trị này; sau khi sửa file phải khởi động lại Uvicorn. Nếu terminal cũ đã đặt `BLENDER_PATH`, hãy mở terminal mới để ưu tiên giá trị từ `.env`. Nếu `BLENDER_PATH` trống, backend thử `PATH`, các thư mục `C:\Blender`, `D:\Blender`, `E:\Blender` và Blender Foundation trong Program Files. Cần cài và bật MPFB2 trong phiên bản Blender được chọn. Script nhận add-on từ `bl_ext.blender_org.mpfb`, `bl_ext.user_default.mpfb` hoặc `mpfb`; nếu tạo MPFB thất bại, job báo lỗi và không xuất mannequin thay thế. Job chạy trong bộ nhớ tiến trình; file GLB nằm ở `data/outputs/blender_body/` và không được commit. Restart backend làm mất job ID.
Backend nhận tối đa hai job Blender đang chờ/chạy; khi bận, UI hiển thị lỗi để người dùng thử lại.

API riêng cho luồng này: `POST /api/body-builder/generate`, `POST /api/body-builder/clothing`, `GET /api/body-builder/jobs/{job_id}`, `GET /api/body-builder/assets/{job_id}.glb`. Trang thử đồ hiện dùng API này cho kết quả 3D, không gọi `/api/tryon/analyze` từ luồng giao diện; các tỷ lệ không phải số đo từ ảnh. Body mặc định có giới tính trung tính và các giá trị MPFB cơ bản ở mức 0,5 như preset “From scratch”; breast size/firmness ở mức 0,55 tương ứng influence 0,10 trong ảnh Blender, chiều cao được co giãn theo số cm chọn. Khi không có asset áo, Blender dựng hình khối theo loại sản phẩm; màu và size thay đổi hình minh họa. Chưa có fitting, mô phỏng vải hay điểm fit từ Blender.

Có thể đặt asset trang phục tùy chọn tại `data/external/clothing/<garment_id>.glb` hoặc `.obj` (ví dụ `demo-tshirt.glb`). Asset cần được dựng quanh body cao khoảng 1,7 m, Z-up trong Blender; hệ thống co giãn theo chiều cao body trước khi xuất Y-up GLB. Nếu thiếu asset thì dùng hình minh họa. File trong `data/external/` đã được Git bỏ qua. Nạp asset hiện chỉ chồng mesh và đổi màu; không tự fit vào body.

## Gọi thử API

Trong CMD hoặc PowerShell, dùng **curl.exe** (tránh alias `curl` của PowerShell).
Thay đường dẫn ảnh bằng file PNG/JPEG thật của bạn, tối đa 5 MiB/16 triệu pixel:

```text
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/api/garments
curl.exe -X POST http://localhost:8000/api/tryon/analyze -F "image=@C:\images\person.jpg;type=image/jpeg" -F "height_cm=170"
```

Lấy `data.body_id` trả về. Tạo file `fit-request.json` bằng editor với nội dung
sau, thay `BODY_ID_FROM_ANALYZE` bằng ID thật:

```json
{"body_id":"BODY_ID_FROM_ANALYZE","garment_id":"demo-tshirt","size":"M"}
```

```text
curl.exe -X POST http://localhost:8000/api/tryon/fit -H "Content-Type: application/json" --data-binary "@fit-request.json"
curl.exe http://localhost:8000/api/jobs/JOB_ID_FROM_FIT
curl.exe http://localhost:8000/api/assets/mock-tryon.glb --output mock-tryon.glb
```

Thay `JOB_ID_FROM_FIT` bằng `data.job_id`. POST fit trả 202/pending; GET job trả
completed hoặc failed khi xong. Mock không sleep nên lần poll đầu có thể completed.
Trong UI, resolve URL asset bằng backend origin; không dùng origin frontend.

GLB đã có sẵn trong `backend/fixtures/assets/`. Tái tạo bằng stdlib:

```text
.\.venv\Scripts\python.exe scripts\generate_mock_glb.py
```

## Chạy kiểm thử

Các lệnh dùng được ở CMD/PowerShell, tương đương job Python trong CI:

```text
.\.venv\Scripts\python.exe -m pytest tests/unit/ tests/e2e/mock/ -m "not slow and not gpu" --verbose
.\.venv\Scripts\python.exe -m ruff check . --select=E9,F63,F7,F82
```

TestClient kiểm tra input, schema, lifecycle/failure job, ID, CORS, GLB có thực,
chống truy cập ngoài asset root và nhãn mock. E2E ở đây là **backend HTTP end-to-end**,
không tuyên bố đã kiểm thử giao diện hay module AI thật.

Workflow chạy trên push/PR vào `dev` và `main`; xem
[CI pipeline](docs/ci-cd/pipeline.md) và
[evidence M3](docs/report/evidence/backend/mock-api-validation.md).
Frontend đã có cấu hình TypeScript và Vite entry; `npm run build` kiểm tra toàn
bộ `src` rồi tạo `dist/`. Trang khởi động dùng `UploadPage` placeholder hiện có;
M5 tiếp tục triển khai giao diện và tích hợp API. Job backend chạy độc lập và
không cài bộ AI nặng.

Trong CMD hoặc PowerShell:

```text
cd frontend
npm.cmd install
npm.cmd run build
npm.cmd run dev
```
