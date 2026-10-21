# Change Impact Log — M3: Tái xử lý job có GLB bị thiếu

- **Vai trò và mục đích:** M3 Backend. Xử lý job image try-on cũ vẫn `completed` trong PostgreSQL nhưng GLB đích đã mất, dẫn tới GET asset 404.
- **File đã sửa:**
  - `backend/services/image_tryon.py`: khi GET job đang completed, xác minh asset file tồn tại. Nếu file thiếu và body GLB còn sẵn, chuyển job về `pending` để worker dựng lại từ input đã lưu. Nếu body GLB cũng mất, đánh dấu body `failed` và job `failed` với mã `BODY_ASSET_NOT_FOUND`.
  - `backend/db/repository.py`: thêm chuyển trạng thái có điều kiện `completed` → `pending` hoặc `completed` → `failed`, giữ tính an toàn khi có nhiều poll đồng thời.
  - `backend/workers/image_tryon.py`: khi asset record còn nhưng file thiếu, cập nhật storage key, kích thước, checksum và trạng thái theo file dựng lại. Conflict vẫn bị chặn khi file cũ còn tồn tại nhưng nội dung khác.
  - `.agents/memory/ACTIVE_CONTEXT.md`: ghi nhận nguyên nhân và hành vi mới.
- **Ảnh hưởng API/schema:** Không đổi endpoint hay response schema. Polling hiện có sẽ nhận trạng thái `pending` trong lúc job được chạy lại; trường hợp body thiếu nhận trạng thái `failed` cùng lỗi cụ thể.
- **Đơn vị/hệ trục:** Không thay đổi.
- **Database/asset:** Không migration. Thay đổi status/result/error của image job; cập nhật metadata asset khi khôi phục. Body thiếu được đánh dấu `failed`, không xóa row để bảo toàn tham chiếu foreign key và lịch sử.
- **Module/owner liên quan:** M3; M5 dùng polling/status và error code hiện có, không cần đổi contract.
- **Xung đột/rủi ro đã xác nhận:** Chưa kiểm tra trực tiếp database và thư mục `data/assets` của runtime. Nếu ảnh đầu vào cũng đã mất, worker sẽ kết thúc job ở trạng thái failed thay vì khôi phục.
- **Kiểm thử:** Chưa chạy test (quy tắc repo không cho agent chạy lệnh terminal/test). Cần restart API và worker, poll lại job ID cũ khi body còn file, và kiểm tra GET URL GLB sau khi job completed.
- **Bàn giao:** Restart cả backend lẫn worker. Với job có body asset mất, tạo body mới rồi submit lại try-on; record body cũ được đánh dấu failed, không bị xóa.
