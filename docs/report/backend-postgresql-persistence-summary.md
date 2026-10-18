# Tổng kết triển khai lưu trữ M3

**Ngày:** 2026-10-18 (Asia/Saigon)  
**Phạm vi:** backend chính `/api/tryon`, metadata body/asset/job và migration.

## Đã đạt được

1. Chọn PostgreSQL làm database chính cho metadata của backend; FastAPI đọc `DATABASE_URL`, Docker Compose có service PostgreSQL và backend chạy migration trước khi phục vụ request.
2. Thêm SQLAlchemy 2 và Alembic. Migration `20261018_0001` tạo bốn bảng `bodies`, `assets`, `tryon_jobs`, `job_steps` cùng khóa ngoại, ràng buộc trạng thái và index truy vấn. Migration khớp SQLAlchemy metadata khi so bằng Alembic autogenerate trên SQLite tạm.
3. `bodies` lưu ID, loại `mock_analyzed`/`mpfb`, trạng thái, nguồn/phương pháp, metadata và lỗi. Service có hàm đăng ký GLB của body MPFB đã có trong kho asset quản lý.
4. `assets` quản lý năm loại `original_image`, `foreground_image`, `mesh`, `texture`, `glb`, kèm trạng thái, khóa lưu trữ tương đối, MIME, kích thước, SHA-256 và liên kết body/job. API chỉ phục vụ GLB đã đăng ký, có tên an toàn và file còn nằm trong thư mục cho phép.
5. `/api/tryon/analyze` lưu metadata body mock. `/api/tryon/fit` lưu job ID, body ID, request, trạng thái, kết quả/lỗi, thời điểm bắt đầu/kết thúc và `duration_ms`. `job_steps` ghi bước nhận request và fit; repository hỗ trợ tạo, đọc, cập nhật trạng thái, lọc truy vấn và thêm step log.
6. Job hoàn tất và GLB mock vẫn tra cứu được sau khi đóng app và tạo app mới trên cùng database. Test còn khởi tạo một Python interpreter mới để kiểm tra qua ranh giới process.

## Bằng chứng kiểm thử

| Kiểm tra | Kết quả quan sát |
| --- | --- |
| `python -m compileall -q backend ...` trong `.venv` | Exit code 0. |
| `pytest tests/unit/backend/test_backend.py tests/unit/backend/test_persistence.py tests/e2e/mock tests/unit/backend/garment3d -q` | **56 passed**; 1 cảnh báo deprecation từ Starlette/httpx. |
| `TC-API-08`: Alembic upgrade trên SQLite tạm, so migration với model | Pass, không có diff metadata. |
| `TC-API-08`: job/asset qua app restart và process mới | Pass; job `completed`, asset HTTP 200, SHA-256 không đổi. |
| Kết nối PostgreSQL `127.0.0.1:5432` | Không kết nối được tại thời điểm kiểm tra; **chưa nghiệm thu PostgreSQL thực tế**. |

Các test SQLite kiểm tra logic persistence và migration ở mức tương thích dialect. Chúng chưa thay thế bài test PostgreSQL với service thật.

## Việc chưa làm tốt / còn thiếu

- `/api/body-builder` vẫn quản lý job MPFB trong bộ nhớ; output của luồng này chưa tự đăng ký vào bảng `bodies/assets`. Hàm đăng ký MPFB hiện dành cho file GLB đã được đặt trong kho asset quản lý.
- `/garment3d` vẫn dùng SQLite và kho asset riêng; chưa hợp nhất vào PostgreSQL chính.
- `BackgroundTasks` vẫn chạy trong tiến trình API. Nếu tiến trình dừng giữa lúc xử lý, job có thể kẹt ở `pending` hoặc `running`; chưa có worker queue, retry, timeout recovery hay idempotency.
- Bảng asset hỗ trợ ảnh gốc, ảnh tách nền, mesh và texture, nhưng `/api/tryon/analyze` vẫn không lưu byte ảnh upload; pipeline ảnh → mesh/texture → GLB chưa nối với repository này.
- Metadata và file asset nằm ở hai nơi. Cần backup/restore cả PostgreSQL lẫn `data/assets/`; hiện chưa có cleanup, đối chiếu SHA định kỳ hoặc chính sách quyền truy cập cho asset người dùng.
- Chưa chạy migration, restart API và đối chiếu dữ liệu trên PostgreSQL thật vì port 5432 không có service tại thời điểm test.

## Bước nghiệm thu tiếp theo

1. Khởi động PostgreSQL phát triển, đặt `DATABASE_URL`, chạy `alembic upgrade head` và kiểm tra bốn bảng.
2. Trên PostgreSQL, tạo body/job/asset, restart tiến trình API thật, kiểm tra `GET /api/jobs/{job_id}` và `GET /api/assets/{asset_name}` cùng hàng trong database.
3. Tích hợp output MPFB và Garment 3D vào kho chung sau khi chốt contract asset/ID; bổ sung worker queue và recovery trước khi coi job đang chạy là bền vững.
