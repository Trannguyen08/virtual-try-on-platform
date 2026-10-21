# Test case M3: Lưu trữ bền vững

| ID | Mục tiêu | Expected | Actual | Trạng thái | Evidence |
| --- | --- | --- | --- | --- | --- |
| TC-API-08 | Migration PostgreSQL/SQLAlchemy; repository body MPFB, 5 loại asset, job và step log; tạo app lần hai trên cùng database. | Có 5 bảng sau migration mới, gồm `image_tryon_jobs`, cùng index/constraint; body/job/GLB còn tra cứu được sau restart. | Bốn bảng cũ đã pass trên SQLite tạm ở đợt trước; bảng thứ năm và PostgreSQL thật chưa chạy trong đợt này. | PASS một phần | [Tổng kết M3](../../report/backend-postgresql-persistence-summary.md) |

Kiểm thử SQLite tạm dùng để xác nhận lifecycle repository và migration tương thích ở mức schema. Nghiệm thu PostgreSQL cần chạy migration và restart API trên PostgreSQL thật, rồi kiểm tra row và file asset vẫn tồn tại.

| ID | Mục tiêu | Expected | Actual | Trạng thái | Evidence |
| --- | --- | --- | --- | --- | --- |
| TC-API-09 | Upload ảnh áo đã chuẩn tỉ lệ cùng body MPFB; job qua restart, claim queue và lỗi có cấu trúc. | 202 sau khi lưu ảnh/job; GET job sau restart; worker claim đúng job; ảnh/body sai không tạo job; lỗi worker chuyển failed. | Chưa chạy; test ở `tests/unit/backend/test_image_tryon.py`. | CHƯA CHẠY | Chờ log người dùng. |
