# Change Impact Log — sửa email khởi tạo pgAdmin

**Thời gian:** 2026-10-18 15:24:10 Asia/Saigon  
**Vai trò:** M3  
**Mục đích:** Sửa lỗi pgAdmin thoát khi khởi tạo do email mẫu không hợp lệ.

## File thay đổi (trước → sau)

| File | Thay đổi |
| --- | --- |
| `docker-compose.yml` | Giá trị fallback `PGADMIN_DEFAULT_EMAIL` từ địa chỉ đuôi `.test` bị pgAdmin từ chối → `admin@tryon.dev`. |
| `.env.example` | Email mẫu khớp giá trị Compose mới. |
| `.env` | Chỉ thay `PGADMIN_DEFAULT_EMAIL` trên máy local; giữ nguyên các biến và mật khẩu khác. File này vẫn bị Git ignore. |

## Ảnh hưởng

- API, Pydantic schema, migration và các bảng PostgreSQL: không đổi.
- Đơn vị, hệ trục, dữ liệu 3D và asset: không đổi.
- M1/M2/M4/M5: không đổi code; chỉ ảnh hưởng đăng nhập công cụ quản trị database của M3.
- Volume PostgreSQL và pgAdmin: không xóa hoặc di chuyển.

## Bằng chứng và giới hạn

- Log container `virtual-try-on-platform-pgadmin-1`: exit code 1; pgAdmin báo địa chỉ email đuôi `.test` là special-use/reserved và từ chối `PGADMIN_DEFAULT_EMAIL`.
- Sau sửa, `docker compose config --quiet`: PASS, exit code 0; PostgreSQL tại `127.0.0.1:5432` vẫn nhận kết nối.
- Chưa chạy lại pgAdmin vì Rule 01 chỉ cho phép terminal đọc/kiểm thử theo ngoại lệ hiện có. Chưa xác nhận HTTP 200 trên cổng 5050; User cần recreate service pgAdmin.
- Email mới là tài khoản mẫu cho local development. Nếu dùng ngoài máy local, owner M3 đặt email của mình và mật khẩu riêng trong `.env`.

## Bàn giao

User chạy `docker compose up -d --no-deps --force-recreate pgadmin`, sau đó kiểm tra `docker compose ps pgadmin` và mở `http://127.0.0.1:5050`.
