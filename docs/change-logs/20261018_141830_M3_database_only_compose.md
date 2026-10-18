# Change Impact Log — M3 database-only Compose

**Thời gian:** 2026-10-18 14:18:30 Asia/Saigon  
**Vai trò:** M3  
**Mục đích:** Cho phép khởi động riêng PostgreSQL và pgAdmin bằng image đã có trên máy.

## File đã thay đổi (trước → sau)

| File | Trước → sau |
| --- | --- |
| `docker-compose.yml` | PostgreSQL dùng tag `postgres:16` chưa có local, chưa có pgAdmin → dùng `postgres:16-alpine`, thêm service pgAdmin, volume riêng, health dependency; publish hai cổng qua `127.0.0.1`. Bỏ thuộc tính `version` đã lỗi thời. |
| `.env.example` | Chưa có cấu hình đăng nhập pgAdmin → thêm email/password mẫu cho môi trường phát triển. |
| `docs/development/run-backend-frontend.md` | Chưa có cách chạy chỉ database → thêm lệnh chọn đúng `postgres pgadmin`, địa chỉ và thông tin kết nối giữa hai container. |

## Ảnh hưởng

- **API/contract/schema:** Không đổi endpoint, Pydantic schema, Alembic migration hay định dạng dữ liệu.
- **Đơn vị/hệ trục:** Không đổi quy ước mét, centimet, Y-up và +Z forward.
- **Database/asset:** PostgreSQL vẫn lưu trong named volume `postgres_data`; pgAdmin có `pgadmin_data`. Không tạo hoặc sửa file asset lớn.
- **Module khác:** Backend/frontend giữ cấu hình Compose hiện tại nhưng không được chọn khi dùng `docker compose up -d postgres pgadmin`. Không thay đổi code M1/M2/M4/M5.

## Kiểm tra và giới hạn

- Đã quan sát local có image `postgres:16-alpine` và `dpage/pgadmin4:latest`; hai container `ChatBox_*` đang dừng và không được sử dụng.
- `docker compose config --quiet`: **PASS**, exit code 0; `docker compose config --images` hiện đúng hai image database/admin bên cạnh tên build backend/frontend.
- Chưa khởi động container trong phiên này. Theo Rule 01 và ngoại lệ terminal đã cấp trước đó (chỉ đọc/kiểm thử), thao tác `docker compose up` dành cho User chạy; vì vậy chưa có log PostgreSQL healthy hay pgAdmin HTTP 200.
- Mật khẩu trong `.env.example` là giá trị mẫu cho môi trường phát triển; owner M3 thay bằng giá trị riêng trong `.env` khi dùng ngoài máy local.

## Bàn giao

M3: chạy `docker compose up -d postgres pgadmin`, kiểm tra health, rồi chạy Alembic khi cần dùng backend. Không xóa volume `postgres_data` khi muốn giữ dữ liệu.
