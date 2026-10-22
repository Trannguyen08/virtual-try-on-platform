# Change Impact Log — M5 — Bắt buộc chọn loại trang phục ảnh

- Thời điểm: 2026-10-21 22:56 Asia/Saigon.
- Vai trò: M5 frontend. Mục đích: ngăn ảnh quần được gửi tới API như áo thun do giá trị mặc định của biểu mẫu.

## Bằng chứng và thay đổi

- Job ảnh mới nhất `itry_c4619f9fb38345668dbfee358759b963` có ảnh đầu vào là quần jeans, nhưng metadata tái dựng ghi `garment_type=tshirt`, `auto_detected=false`, chiều dài tham chiếu 70 cm. Giao diện trước đó mặc định `tshirt` khi không có sản phẩm ban đầu; API chuyển giá trị này tới bộ dựng 3D.
- Sửa `frontend/src/pages/tryon/ImageTryOnPage.tsx`: `initialType` trả giá trị rỗng khi không có danh mục; sau khi đổi ảnh mặt trước, xóa loại đã chọn; biểu mẫu bắt buộc chọn loại, khóa nút gửi nếu chưa chọn; đổi loại hoặc ảnh sẽ bỏ job và lỗi cũ; hiện loại đã xử lý ở kết quả.
- File mới `docs/change-logs/20261021_225600_M5_require_image_garment_type.md`: ghi nhận đợt sửa này.

## Tác động

- API/schema: không đổi endpoint, request hoặc response. Chỉ thay điều kiện cho phép gửi request ở UI; `garment_type` vẫn là một trong sáu giá trị hợp lệ.
- Đơn vị/hệ trục: không đổi. Giá trị chiều dài cm được chọn theo loại sau khi người dùng chọn.
- Database/asset: không đổi dữ liệu server hoặc GLB cũ. UI xóa job cũ khỏi localStorage khi ảnh/loại thay đổi; job và scene đã tạo trên server vẫn tồn tại.
- Module khác: M3/M2 không đổi code; M2 tiếp tục tin `garment_type` của request. Nguy cơ còn lại: nếu người dùng chủ động chọn sai loại, frontend không phân loại ảnh để phát hiện. Có thể cần M2 bổ sung kiểm tra mismatch ở một đợt riêng.
- Xung đột đã xác nhận: không có trong file M5 được sửa. Chưa kiểm tra build và luồng browser sau sửa.

## Kiểm tra và bàn giao

- Đã đối chiếu ảnh đầu vào và metadata của job thực tế, cùng luồng gửi `garment_type` ở frontend/backend bằng đọc mã nguồn.
- Chưa chạy test/build theo Rule 01 của repo. Người dùng cần tải lại frontend, tải ảnh quần, chọn **Quần**, tạo job mới; GLB của job cũ không tự thay đổi.
