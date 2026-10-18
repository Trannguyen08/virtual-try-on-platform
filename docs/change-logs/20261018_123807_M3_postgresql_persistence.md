# Change Impact Log — M3 PostgreSQL persistence

**Thời gian:** 2026-10-18 12:38:07 Asia/Saigon  
**Vai trò:** M3  
**Mục đích:** Lưu metadata body, asset và job của backend chính qua restart; tạo migration và bằng chứng kiểm thử.

## File đã thay đổi (trước → sau)

| File | Trước → sau |
| --- | --- |
| `backend/requirements.txt` | Chưa có DB ORM/migration/driver → khai báo SQLAlchemy, Alembic, psycopg. |
| `backend/core/config.py` | Chưa có DB/managed asset settings → thêm `database_url`, `managed_asset_dir` và kiểm tra URL rỗng. |
| `backend/db/__init__.py` | Chưa tồn tại → package DB. |
| `backend/db/models.py` | Chưa tồn tại → `BodyRecord`, `AssetRecord`, `JobRecord`, `JobStepRecord` với FK, index, trạng thái và timestamp. |
| `backend/db/session.py` | Chưa tồn tại → engine và session factory. |
| `backend/db/repository.py` | Chưa tồn tại → CRUD/truy vấn body/asset/job, chuyển trạng thái job và step log. |
| `backend/db/migrations/env.py` | Chưa tồn tại → Alembic đọc `DATABASE_URL`, metadata SQLAlchemy. |
| `backend/db/migrations/script.py.mako` | Chưa tồn tại → template revision. |
| `backend/db/migrations/versions/20261018_0001_persistent_metadata.py` | Chưa tồn tại → migration tạo/bỏ bốn bảng. |
| `backend/services/storage.py` | Chưa tồn tại → đăng ký asset có kiểm tra phạm vi, đăng ký MPFB body, seed fixture và tra GLB an toàn. |
| `backend/services/job_manager.py` | Dict trong process → đọc/ghi job qua `JobRepository`; giữ BackgroundTasks. |
| `backend/services/orchestrator.py` | Dict body trong process → `StorageService` lưu/đọc body. |
| `backend/api/assets.py` | Chỉ kiểm tra allowlist file → tra asset đã đăng ký trong DB. |
| `backend/main.py` | Không có engine → khởi tạo repository/storage, seed fixture tại lifespan, dispose engine khi dừng. |
| `alembic.ini` | Chưa tồn tại → cấu hình migration. |
| `.env.example` | Chưa có database URL → ví dụ URL PostgreSQL phát triển. |
| `docker-compose.yml` | Chưa có PostgreSQL → service PostgreSQL, healthcheck, volume và kết nối backend. |
| `docker/backend/Dockerfile` | Cài root requirements trước khi copy toàn repo → cài backend requirements sau copy, chạy migration trước Uvicorn. |
| `.dockerignore` | Chưa tồn tại → loại `.env`, data, venv, weights và cache khỏi build context. |
| `tests/conftest.py` | Test app không có DB → fixture SQLite riêng cho test backend. |
| `tests/unit/backend/test_backend.py` | Test kỳ vọng restart mất job → kiểm tra job/body còn và gắn TC-API-03. |
| `tests/unit/backend/test_persistence.py` | Chưa tồn tại → migration, repository, MPFB, asset và restart qua process mới; ca lỗi asset. |
| `docs/api/api-contract.md` | Mô tả body/job process-local → mô tả metadata bền vững và giới hạn BackgroundTasks. |
| `docs/development/run-backend-frontend.md` | Chưa có bước DB → hướng dẫn PostgreSQL, migration, lưu ý các luồng còn tách biệt. |
| `docs/testing/test-cases/test-cases-backend-persistence.md` | Chưa tồn tại → TC-API-08 và trạng thái nghiệm thu một phần. |
| `docs/testing/test-cases/test-cases-fit-ai.md` | TC-API-03 ghi restart mất job → cập nhật kết quả hiện tại và liên kết evidence mới. |
| `docs/report/backend-postgresql-persistence-summary.md` | Chưa tồn tại → tổng kết đạt được, giới hạn và kết quả test. |

## Ảnh hưởng

- **API/contract:** Endpoint và cấu trúc envelope giữ nguyên. Nội dung `Job.notes` đổi từ cảnh báo in-memory sang mô tả job state persisted. `GET /api/jobs/{id}` có thể đọc job đã hoàn tất sau restart. `GET /api/assets/{name}` cần asset có row DB và file hợp lệ.
- **Schema/database:** Bốn bảng mới trên PostgreSQL chính; phải chạy `alembic upgrade head` trước startup. Dữ liệu job process-local cũ không có nguồn để migrate. `/garment3d` vẫn SQLite riêng.
- **Đơn vị/hệ trục:** Không đổi số đo cm ở API hay quy ước GLB mét, Y-up, +Z forward; tầng này chỉ lưu metadata và tham chiếu file.
- **Asset/dữ liệu lớn:** Bảng lưu đường dẫn tương đối, kích thước và SHA-256; không đưa byte ảnh/mesh vào PostgreSQL. `.dockerignore` ngăn đưa data/weights/.env vào image. File tại `data/assets/` cần backup cùng DB.
- **Module liên quan:** M1 cần đăng ký output MPFB vào kho chung; M2 cần tích hợp output ảnh/mesh/texture/GLB và cân nhắc chuyển `/garment3d` khỏi SQLite; M5 không phải đổi field polling nhưng có thể tra job sau restart; M4 chưa bị thay đổi code. Chưa kiểm tra end-to-end module thật.

## Xung đột và rủi ro

- Contract cũ nói restart mất job; đã sửa phần mô tả và TC-API-03. Bằng chứng lịch sử 2026-09-28 chỉ hợp lệ cho bản cũ.
- `BackgroundTasks` không phục hồi tác vụ dở dang. Job `pending/running` có thể kẹt sau crash; cần worker, timeout và recovery.
- Asset có thể mất khỏi disk dù row DB còn; API trả 404 và đánh dấu thiếu khi phát hiện. Chưa có cơ chế backup/cleanup hay kiểm tra SHA định kỳ.
- PostgreSQL thật chưa chạy trên máy kiểm thử; tương thích thực tế, Docker Compose và restart Uvicorn còn phải nghiệm thu.

## Kiểm thử và bàn giao

- `compileall` backend và test Python: **PASS**, exit code 0.
- `pytest tests/unit/backend/test_backend.py tests/unit/backend/test_persistence.py tests/e2e/mock tests/unit/backend/garment3d -q`: **56 passed**. Một cảnh báo deprecation Starlette/httpx. Bằng chứng chi tiết trong [báo cáo](../report/backend-postgresql-persistence-summary.md).
- `Test-NetConnection 127.0.0.1:5432`: **False**; chưa test PostgreSQL thật.
- Owner bàn giao: M3 vận hành migration/worker và hợp nhất `/api/body-builder`, `/garment3d`; M1/M2 xác nhận asset contract; M5 xác nhận polling sau restart trên môi trường tích hợp.
