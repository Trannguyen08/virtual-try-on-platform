# Virtual Try-On Platform

Mục tiêu dự án: thử đồ 3D và gợi ý size. **Hiện đã có backend mock MVP**, chưa có
pipeline xử lý ảnh/AI thật hay frontend hoàn chỉnh. Số đo/nhãn fit và các GLB
hình khối là dữ liệu demo, luôn có `source: "mock"`; score/confidence là `null`.

Contract để M1/M2/M4/M5 tích hợp: [docs/api/api-contract.md](docs/api/api-contract.md).
Tổng quan và kiến trúc hệ thống: [docs/project-overview.md](docs/project-overview.md) | [docs/architecture/system-architecture.md](docs/architecture/system-architecture.md).

## Chạy backend trên Windows

Python 3.10+; chạy từ thư mục gốc repo. Các lệnh dưới dùng được trong **CMD và
PowerShell**, không cần activate venv. Nếu `.venv` đã tồn tại, bỏ qua lệnh tạo.

```text
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
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

Không tự đọc `.env`; dùng env của shell hoặc `uvicorn --env-file .env`.

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
