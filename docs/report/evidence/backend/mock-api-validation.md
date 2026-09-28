# M3 backend mock — evidence local

Ngày: 2026-09-28. Nhánh: `feature/backend-mock-api`. Terminal: PowerShell trên
Windows; Python 3.10.11. Working tree sạch trước khi làm; không có AGENTS.md.
Không push, PR, merge hay chạy GitHub Actions trong đợt này.

## Lệnh và kết quả thực tế

Từ repo root:

```text
.\.venv\Scripts\python.exe -m pip install -r backend/requirements-dev.txt
.\.venv\Scripts\python.exe scripts/generate_mock_glb.py
.\.venv\Scripts\python.exe -m pytest tests/unit/ tests/e2e/mock/ -m "not slow and not gpu" --verbose
.\.venv\Scripts\python.exe -m ruff check . --select=E9,F63,F7,F82
git diff --check
```

- Dependency: thành công; FastAPI 0.141.1, Pydantic 2.13.5, pytest 9.1.1,
  httpx 0.28.1, Pillow 12.3.0, python-multipart 0.0.32, Ruff 0.16.9.
- Generator: body 1776 bytes, t-shirt 1528 bytes, try-on 2048 bytes.
- Pytest khi hoàn tất backend (trước khi bổ sung frontend entry):

```text
collected 51 items
tests/unit/backend/test_backend.py: 50 passed
tests/e2e/mock/test_mock_e2e.py: 1 passed
51 passed, 1 warning in 2.57s
```

- Warning từ dependency: `StarletteDeprecationWarning: Using httpx with
  starlette.testclient is deprecated; install httpx2 instead.` Không suppress
  warning, không làm test fail. Nên rà lại TestClient dependency khi nâng phiên bản.
- Ruff theo đúng rule CI: `All checks passed!`. Ruff mặc định trên các file Python
  vừa sửa cũng pass; không sửa lint tồn tại từ trước ở placeholder ngoài phạm vi.
- `git diff --check`: exit 0.
- Sáu ví dụ JSON trong API contract đã validate bằng đúng Pydantic schema triển khai.
- Lần chạy test ban đầu gặp lỗi fixture setup vì pytest tự dùng payload 5 MiB làm
  parameter ID trên Windows; đã đặt ID ngắn cho parameter, giữ nguyên test payload.

Trong thư mục frontend, lần kiểm tra ban đầu trước khi bổ sung config/entry:

```text
npm.cmd install --package-lock=false --ignore-scripts --no-audit --no-fund
npm.cmd run build
.\node_modules\.bin\tsc.cmd --noEmit --strict --skipLibCheck --lib ES2020,DOM src/api/types.ts
```

- Install thành công, không tạo lockfile; có warning dependency three-mesh-bvh cũ.
- Build ban đầu **FAIL, exit 1**: `tsc` in help vì thiếu tsconfig.json. Khi đó repo
  cũng thiếu index.html. Lỗi này đã được xử lý trong đợt bổ sung dưới đây.
- Type envelope được compile riêng: PASS, exit 0.
- Kiểm tra GLB độc lập bằng Three.js GLTFLoader.parseAsync từ dependency frontend:
  body 6 mesh, t-shirt 3 mesh, try-on 9 mesh; cả ba parse thành công. Đây là kiểm
  tra loader, chưa phải kiểm tra hiển thị qua giao diện/WebGL.

## Bổ sung frontend config/entry theo yêu cầu tiếp theo

- Thêm `frontend/tsconfig.json`: strict TypeScript, React JSX, Vite env types,
  kiểm tra toàn bộ `src`, không emit JS từ tsc; Vite thực hiện bundling.
- Thêm `frontend/index.html` và `frontend/src/main.tsx`, mount `UploadPage`
  placeholder đã có bằng React createRoot. Không thay đổi logic backend/API.
- Chạy `npm.cmd run build` trong `frontend`: **PASS, exit 0** trên Node 22.22.2,
  TypeScript 5.9.3, Vite 5.4.21; 30 modules, `dist/index.html` và JS bundle được
  tạo thành công, Vite build 2.99s. CI vẫn dùng Node 20 như workflow hiện có.
- Chạy lại lệnh pytest của CI: **51 passed, 1 warning in 2.90s**; warning
  TestClient không thay đổi. Ruff theo rule CI: **All checks passed!**.
- Chưa push/PR, nên đây là kết quả local, chưa phải kết quả GitHub Actions.

## Ma trận kiểm thử

| Phạm vi | Expected | Actual |
| --- | --- | --- |
| Health/catalog/OpenAPI | Giữ healthy; áo S/M/L/XL; đủ route/schema | PASS |
| Analyze hợp lệ | PNG/JPEG; echo height; số đo cố định, source mock, confidence null | PASS |
| Analyze sai | Thiếu/NaN/ngoài dải => 422; giả/rỗng/hỏng => 400; MIME lạ => 415; quá bytes/pixel => 413 | PASS |
| Fit/job | 202 pending; GET đúng job/request/result; đủ bốn size, ID riêng | PASS |
| Fit sai | Body/garment không tồn tại => 404; size/JSON sai => 422; size không thuộc chart => 422 | PASS |
| Lifecycle | pending -> running -> completed; duplicate dispatch không chạy lại | PASS |
| Failure | Exception provider => job failed có PROCESSING_FAILED; không lộ exception | PASS |
| API unexpected error | HTTP 500 cùng envelope, không lộ nội bộ | PASS |
| Store | App instance mới mất body/job cũ, trả 404 | PASS |
| Assets | Tải được mọi URL; GLB header/chunks/bounds đúng; generator byte-for-byte | PASS |
| Asset security | Traversal slash/backslash/encoded/absolute/unregistered bị từ chối; resolved path ngoài root bị từ chối | PASS |
| Missing asset | Trả null, không phát URL giả; GET 404 | PASS |
| CORS | Chỉ origin allowlist; chặn wildcard config | PASS |
| HTTP mock E2E | Hai body -> hai job -> kết quả đúng -> tải mọi GLB | PASS |

## Giới hạn

Không có test/thuật toán AI thật, không frontend E2E hay validation độ chính xác
số đo. Geometry cố định theo hộp, không scale theo người/size. Job/body process-local,
không TTL/persistence/multi-worker. Chưa test triển khai Linux thực tế/GitHub Actions.
Backend CI đã cấu hình chạy cùng lệnh test ở trên; lỗi frontend thiếu config/entry
đã được sửa và build local pass. Dependency dùng khoảng version, chưa lock toàn
bộ môi trường.
