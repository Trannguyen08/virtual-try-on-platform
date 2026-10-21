# Change Impact Log — M3: Khôi phục asset image try-on

- **Vai trò và mục đích:** M3 Backend. Sửa đường dẫn lưu GLB image try-on và cho phép worker khôi phục file bị thiếu khi metadata asset còn nguyên.
- **File đã sửa:**
  - `backend/workers/image_tryon.py`: trước đây asset mới trỏ tới file scene tên ngẫu nhiên bên trong thư mục xử lý; nay worker publish bản GLB với tên ổn định `tryon-{job_id}.glb`. Khi đã có asset record nhưng file không còn, chỉ phục hồi nếu kích thước và SHA-256 của output khớp metadata asset hiện hữu.
  - `backend/db/repository.py`: thêm `AssetRepository.restore_managed_glb` để chuyển storage key sang file đã khôi phục, cập nhật kích thước/checksum và đặt trạng thái `available`.
  - `.agents/memory/ACTIVE_CONTEXT.md`: ghi nhận thay đổi và việc cần xác minh.
- **Ảnh hưởng API/schema:** Không đổi endpoint, response hay schema. URL public tiếp tục là `/api/assets/tryon-{job_id}.glb`.
- **Đơn vị/hệ trục:** Không thay đổi; GLB tiếp tục theo contract hiện hành.
- **Database/asset:** Không migration. Có cập nhật metadata của asset row hiện hữu trong trường hợp worker phục hồi thành công; file canonical mới nằm dưới managed asset root.
- **Module/owner liên quan:** M3 sở hữu worker và repository. M5 không cần đổi contract hoặc URL.
- **Xung đột/rủi ro đã xác nhận:** Chưa kiểm tra trạng thái job và nội dung file trên máy người dùng; vì vậy chưa xác nhận nguyên nhân cụ thể của asset 404 đã gửi. Worker chỉ tự phục hồi asset đã đăng ký nếu output tái tạo khớp chính xác size và SHA-256; nếu không khớp, job báo `ASSET_CONFLICT`.
- **Kiểm thử:** Chưa chạy test (quy tắc repo không cho agent chạy lệnh terminal/test). Cần xác minh job hoàn tất, sau đó GET asset URL trả GLB thành công; đồng thời kiểm tra retry khi file bị thiếu.
- **Bàn giao:** Chạy lại backend và worker để nạp code mới, gửi một job mới và xác nhận GET asset. Job đã completed trước đó không tự được chạy lại; nếu file cũ đã bị xóa thì cần job mới để tạo GLB.
