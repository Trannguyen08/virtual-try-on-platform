# M3 — Nạp BLENDER_PATH từ .env khi chạy backend

Thời điểm: 2026-10-14 17:03:57 (Asia/Saigon).

## Vai trò và mục đích

M3 cập nhật cấu hình khởi động backend để người dùng lưu đường dẫn Blender trong `.env` thay vì đặt biến PowerShell mỗi lần chạy.

## File thay đổi: trước → sau

- `.env`: `BLENDER_PATH = D:\Blender\blender.exe` → `BLENDER_PATH=D:/Blender/blender.exe`; giữ các khóa khác nguyên trạng.
- `.env.example`: ví dụ chứa đường dẫn riêng của máy và khoảng trắng quanh dấu `=` → khóa `BLENDER_PATH=` để trống, có hướng dẫn đặt đường dẫn tuyệt đối.
- `.gitignore`: dòng `.env` bị comment → bỏ comment để tránh thêm file cấu hình cục bộ vào Git ở các lần sau. Trạng thái Git hiện tại của file chưa được kiểm tra theo Rule 01.
- `docs/development/run-backend-frontend.md`: lệnh chạy cần đặt `$env:BLENDER_PATH` ở terminal → lệnh Uvicorn thêm `--env-file .env`, giải thích khởi động lại khi sửa file.
- `README.md`: quickstart không nạp `.env`, phần Blender đặt biến PowerShell → quickstart dùng `--env-file .env`, phần Blender minh họa cú pháp `BLENDER_PATH` trong file.
- File log này: trước chưa tồn tại → ghi thay đổi và tác động.

## Ảnh hưởng tích hợp

- API/schema/đơn vị/database/asset: không đổi endpoint, payload, đơn vị, nơi lưu job hay GLB. `BLENDER_PATH` được truyền vào môi trường backend lúc Uvicorn khởi động.
- Module M1/M5: không đổi script MPFB hay viewer; đường dẫn Blender được chọn từ `.env` khi chạy theo tài liệu. Các tiến trình backend cũ cần khởi động lại; sửa `.env` không tự cập nhật tiến trình đang chạy.

## Phối hợp, xung đột và rủi ro

- Owner: M3 xác nhận cấu hình backend; M1 xác nhận Blender được chọn có MPFB2. M5 không cần đổi contract.
- Xung đột đã xác nhận: `.env` đã có `BLENDER_PATH`, nhưng lệnh Uvicorn trước đó không nạp file; vì vậy giá trị trong file không đến được `os.getenv` của backend.
- Rủi ro: nếu người dùng chạy backend bằng lệnh khác không có `--env-file .env`, file vẫn không được nạp. Biến `BLENDER_PATH` đã tồn tại trong terminal được `python-dotenv` ưu tiên hơn giá trị trong file; dùng terminal mới khi đổi sang `.env`. Chưa kiểm tra `.env` có từng được Git theo dõi hay không; `.gitignore` chỉ ngăn thêm mới.

## Kiểm thử và bàn giao

- Đã đọc mã Uvicorn và gói `dotenv` có sẵn trong `.venv`; chưa chạy backend, test hoặc Blender theo Rule 01.
- Người dùng dừng backend, chạy lại lệnh có `--env-file .env` từ gốc repo và tạo job body mới. Nếu vẫn lỗi, gửi log job mới.
