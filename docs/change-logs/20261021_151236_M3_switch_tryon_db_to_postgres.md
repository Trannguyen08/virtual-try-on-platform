# Change Impact Log — M3 chuyển database try-on sang PostgreSQL

**Thời gian:** 2026-10-21 15:12:36 Asia/Saigon  
**Vai trò:** M3  
**Mục đích:** Nạp cấu hình `.env` cho backend/Alembic, dùng PostgreSQL Docker thay cho SQLite của database try-on và loại bỏ file SQLite try-on cũ theo yêu cầu.

## File thay đổi (trước → sau)

| File | Trước → sau |
| --- | --- |
| `backend/core/config.py` | Không nạp `.env`; khi `DATABASE_URL` chưa có trong process environment sẽ rơi về `sqlite+pysqlite:///./data/tryon.sqlite3` → nạp `.env` tại repo root (không ghi đè biến môi trường đã đặt) và mặc định PostgreSQL tại `localhost:5432/tryon`. |
| `data/tryon.sqlite3` | File SQLite try-on cũ còn tồn tại (106,496 bytes; nội dung chưa kiểm tra) → đã xóa sau khi migration PostgreSQL hoàn tất. |
| `.agents/memory/ACTIVE_CONTEXT.md` | Ngữ cảnh trước đó → ghi nhận cấu hình, revision DB và SQLite độc lập còn lại. |

## Ảnh hưởng

- **API/schema:** Không đổi endpoint, schema hoặc payload.
- **Database:** Backend và Alembic đọc cùng `DATABASE_URL`. PostgreSQL Docker `virtual-try-on-platform-postgres-1` được xác nhận healthy; Alembic đã lên `20261018_0002 (head)`.
- **SQLite:** `data/tryon.sqlite3` đã xóa. `data/garment3d.sqlite3` vẫn còn vì `backend/garment3d` có repository SQLite riêng và chưa được chuyển đổi trong thay đổi này.
- **Đơn vị/hệ trục:** Không đổi; m nội bộ, cm ngoại vi, Y-up, +Z forward.
- **Asset:** Không thay đổi asset hoặc file nặng.
- **Module khác:** M1/M2/M4/M5 không đổi. Thay đổi có thể ảnh hưởng môi trường backend Docker do config dùng `.env`; image backend đã bao gồm `python-dotenv` qua `backend/garment3d/requirements.txt`.
- **Owner phối hợp:** M3; nếu cần loại bỏ toàn bộ SQLite trong runtime thì cần một thay đổi riêng chuyển `backend/garment3d` sang PostgreSQL.

## Kiểm tra

- PostgreSQL container: `Up`, health `healthy`; cổng `127.0.0.1:5432` mở.
- `python -m alembic upgrade head`: hoàn tất thành công.
- `python -m alembic current`: `20261018_0002 (head)`.
- Automated tests: chưa chạy.

## Bàn giao

Backend try-on dùng PostgreSQL. SQLite cũ của try-on đã xóa; SQLite độc lập của Garment3D vẫn hoạt động và còn nguyên. Nếu yêu cầu “không còn SQLite nào” áp dụng cả Garment3D, cần chuyển repository đó sang PostgreSQL trước khi xóa file còn lại.
