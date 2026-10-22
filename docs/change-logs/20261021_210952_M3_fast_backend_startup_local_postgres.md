# Change Impact Log — rút ngắn startup backend với PostgreSQL local

- Thời gian: 2026-10-21 21:09:52 Asia/Saigon
- Vai trò: M3; owner bị ảnh hưởng: M3 vận hành backend, M5 dùng API sau startup.
- Mục đích: xử lý thời gian chờ tại `Waiting for application startup.` trên máy Windows hiện tại.

## File thay đổi (trước → sau)

- `.env` (local, được Git ignore): host của `DATABASE_URL` là `localhost` → `127.0.0.1`; giữ nguyên các phần khác và không ghi giá trị bí mật vào log.
- `.env.example`: URL PostgreSQL mẫu dùng `localhost` → `127.0.0.1` cho backend chạy trên host Windows.
- `backend/core/config.py` (`Settings.database_url`): fallback host `localhost` → `127.0.0.1` khi không có `DATABASE_URL`.
- `backend/db/session.py` (`make_engine`): PostgreSQL chưa giới hạn thời gian kết nối → thêm `connect_timeout=5` giây; nhánh SQLite không đổi.
- `backend/main.py` (`create_app.lifespan`): startup không báo từng bước → log thời gian kiểm tra schema, đăng ký fixture và khởi tạo Garment 3D qua logger Uvicorn; không log URL/mật khẩu DB.
- `docs/development/run-backend-frontend.md`: chưa nêu khác biệt phân giải `localhost` trên Windows → hướng dẫn dùng `127.0.0.1` với PostgreSQL Docker publish IPv4.
- `.agents/memory/ACTIVE_CONTEXT.md` (local, được Git ignore): thêm chẩn đoán và kết quả sửa.
- `docs/change-logs/20261021_210952_M3_fast_backend_startup_local_postgres.md`: chưa tồn tại → log này.

## Căn cứ, contract và rủi ro

- `.env` trước sửa trỏ PostgreSQL local qua `localhost`. Máy phân giải `localhost` thành `::1` trước `127.0.0.1`; Docker chỉ nghe trên `127.0.0.1:5432`. Kết nối SQLAlchemy với host cũ chờ quá 20 giây; cùng URL chỉ đổi host thành `127.0.0.1` hoàn tất `SELECT 1` trong khoảng 0,42 giây. PostgreSQL Docker báo healthy.
- Không đổi endpoint, schema, response, database schema, đơn vị m/cm hay trục Y-up/+Z forward. Có đổi hành vi timeout kết nối PostgreSQL: báo lỗi sau khoảng 5 giây cho mỗi lần thử host khi không kết nối được, thay vì chờ lâu không rõ nguyên nhân.
- `backend/main.py` vẫn gọi `Base.metadata.create_all`, seed fixture và Garment 3D như trước; log mới giúp nhận biết bước chậm. Không thay đổi job/asset. Backend chạy trong Docker dùng hostname service `postgres` từ cấu hình riêng, không bị thay bằng fallback local.
- Nguy cơ còn lại: môi trường PostgreSQL từ xa chậm hơn 5 giây có thể cần timeout riêng; chưa kiểm tra môi trường đó. Backend đã mở trước khi sửa `.env` cần restart để nạp host mới.

## Xác minh

- Trước sửa: thử kết nối qua `Settings().database_url` với `localhost` không hoàn tất sau hơn 20 giây; tiến trình chẩn đoán đã dừng. Kết nối trực tiếp IPv4 và `SELECT 1`: khoảng 0,42 giây.
- Sau sửa: `SELECT 1` qua `Settings().database_url` và `make_engine`: 0,36 giây. `TestClient(create_app())` khởi tạo lifespan: 0,33 giây; `GET /health`: HTTP 200.
- `git diff --check`: không có lỗi whitespace. Chưa chạy pytest hoặc Blender; các phép đo trên chỉ xác minh startup và kết nối DB trên máy này, không thay thế bộ test API.
- Bàn giao M3: khởi động lại Uvicorn bằng terminal của user và quan sát log ba bước; nếu bước nào còn lâu, đối chiếu thời gian in ra. Chưa commit/push thay đổi này.
