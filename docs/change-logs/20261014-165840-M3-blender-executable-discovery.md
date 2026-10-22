# M3 — Tự tìm Blender executable cho body-builder job

Thời điểm: 2026-10-14 16:58:40 (Asia/Saigon).

## Vai trò và mục đích

M3 sửa cách backend tìm Blender sau khi người dùng báo job lỗi `FileNotFoundError [WinError 2]` tại `subprocess.run`. Đã xác nhận file `D:\Blender\blender.exe` tồn tại; mở Blender GUI không làm tên lệnh `blender` xuất hiện trong PATH của backend.

## File thay đổi: trước → sau

- `backend/services/blender_body.py`: `BlenderBodyJobs.run` chỉ dùng `BLENDER_PATH` hoặc chuỗi `blender` → thêm `find_blender_executable()`, ưu tiên `BLENDER_PATH`, sau đó PATH, `C:/Blender`, `D:/Blender`, `E:/Blender` và bản cài trong Program Files. Nếu đường dẫn cấu hình sai hoặc không tìm được file, job trả thông báo cụ thể; log thiếu executable không còn in traceback đường dẫn máy.
- `docs/development/run-backend-frontend.md`: đã có ví dụ `BLENDER_PATH` nhưng chưa giải thích terminal/backend → ghi rõ phải đặt biến trong terminal chạy Uvicorn và khởi động lại; mô tả các vị trí được tự dò.
- `README.md`: phần Blender chỉ hướng dẫn env/PATH → bổ sung cách tự dò và yêu cầu khởi động lại backend khi đổi env.
- File log này: trước chưa tồn tại → ghi nguyên nhân, thay đổi và tác động.

## Ảnh hưởng tích hợp

- API/schema: giữ nguyên endpoint và kiểu response; chỉ đổi thông báo lỗi của job khi không tìm thấy `blender.exe`.
- Đơn vị, database, asset: không đổi định dạng GLB, đơn vị hay nơi lưu job/asset; job vẫn trong bộ nhớ.
- Module khác: M5 hiển thị chuỗi `job.error` có nội dung mới. M1 tiếp tục chạy script MPFB qua Blender được backend chọn; không sửa thuật toán dựng mesh.

## Phối hợp, xung đột và rủi ro

- Owner: M3 xác nhận cách tìm executable; M5 xác nhận thông báo lỗi hiển thị; M1 xác nhận Blender được chọn có MPFB2.
- Xung đột đã xác nhận: tài liệu trước có ví dụ đường dẫn đúng, nhưng backend người dùng đã khởi động không nhận biến và gọi tên `blender`, gây `WinError 2`. Đã thêm tự dò đúng vị trí cài trên máy.
- Nguy cơ: nếu có nhiều bản Blender, thứ tự là `BLENDER_PATH` → PATH → thư mục cài phổ biến. Bản được chọn có thể không có MPFB2; đặt `BLENDER_PATH` rõ ràng để ép đúng bản. Việc thực thi và nạp add-on chưa được kiểm chứng sau sửa.

## Kiểm thử và bàn giao

- Bằng chứng lỗi trước sửa: log `FileNotFoundError [WinError 2]` do người dùng gửi; đã xác nhận bằng thao tác đọc rằng `D:\Blender\blender.exe` tồn tại.
- Chưa chạy backend, test hoặc Blender headless sau sửa theo Rule 01. Người dùng khởi động lại backend, tạo body mới; nếu có lỗi tiếp theo, gửi thông báo job/log mới để kiểm tra giai đoạn MPFB.
