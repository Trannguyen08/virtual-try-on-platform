# Test case M3: Lưu trữ bền vững

| ID | Mục tiêu | Expected | Actual | Trạng thái | Evidence |
| --- | --- | --- | --- | --- | --- |
| TC-API-08 | Migration PostgreSQL/SQLAlchemy; repository body MPFB, 5 loại asset, job và step log; tạo app lần hai trên cùng database. | Có 4 bảng và index/constraint; body/job/GLB còn tra cứu được sau restart; job hoàn tất có thời gian xử lý và step log. | Pass trên SQLite tạm, gồm process mới; chưa có service PostgreSQL để nghiệm thu dialect thật. | PASS một phần | [Tổng kết M3](../../report/backend-postgresql-persistence-summary.md) |

Kiểm thử SQLite tạm dùng để xác nhận lifecycle repository và migration tương thích ở mức schema. Nghiệm thu PostgreSQL cần chạy migration và restart API trên PostgreSQL thật, rồi kiểm tra row và file asset vẫn tồn tại.
