# Kiểm tra phòng phối đồ

Trạng thái: **Build PASS; các kịch bản browser bên dưới chưa chạy**. Đây là kịch bản bàn giao, chưa phải bằng chứng PASS cho UI/E2E.

Build: User cấp quyền chạy `npm.cmd run build`, kết quả cuối exit 0, TypeScript + Vite 5.4.21, 669 modules, Vite 14.03s. Có cảnh báo main chunk 998.45 kB (gzip 272.36 kB).

Chạy backend, worker và frontend theo `docs/development/run-backend-frontend.md`.
Tại `frontend`, chạy `npm.cmd run build` để kiểm tra TypeScript và Vite trước khi kiểm tra browser.

| ID | Thao tác | Kết quả cần xác nhận |
| --- | --- | --- |
| TC-WEB-OUTFIT-01 | Mở `/try-on`, mở camera, chụp ảnh rồi tạo model từ thông số | Có ảnh xem trước; model được tạo qua API; UI nói rõ ảnh chưa dùng để tái dựng body; camera dừng sau khi đóng hoặc tạo model |
| TC-WEB-OUTFIT-02 | Từ danh mục, chọn thử một áo; trong phòng thử chọn thêm quần; áp dụng | Đúng sản phẩm được chọn; cả áo và quần xuất hiện trên cùng model, chỉ một body; không căn giữa từng garment riêng |
| TC-WEB-OUTFIT-03 | Khi đang mặc áo A và quần B, chọn áo C rồi áp dụng; sau đó đổi riêng quần | Giữ B khi đổi áo; giữ C khi đổi quần; món chưa đổi không tạo lại job |
| TC-WEB-OUTFIT-04 | Chọn “Ảnh sản phẩm ngoài”, tải ảnh áo và ảnh quần vào hai slot khác nhau | File và chiều dài từng món độc lập; gửi đúng `garment_type` và `reference_value_cm` cho từng job |
| TC-WEB-OUTFIT-05 | Nhập chiều dài 0/251 hoặc chưa chọn ảnh mặt trước | Nút thử đồ bị khóa; hướng dẫn bổ sung ảnh rõ ràng; không gửi yêu cầu sai |
| TC-WEB-OUTFIT-06 | Chọn váy liền; tiếp tục chọn lại một áo | Váy liền thay cả áo/quần; chọn áo loại bỏ váy liền; không giữ lớp xung đột trên model |
| TC-WEB-OUTFIT-07 | Bỏ áo trong bộ đang mặc | Áo biến mất, quần và model còn; không gọi Blender để bỏ món |
| TC-WEB-OUTFIT-08 | Từ bộ đang mặc, quay lại danh mục và chọn một sản phẩm khác | Khôi phục model và món còn lại; kết quả upload hoàn tất vẫn được giữ trong phiên; ảnh cá nhân/file không lưu vào storage |
| TC-WEB-OUTFIT-09 | Tải lại trang khi job ảnh đang chạy rồi bấm tiếp tục | Tiếp tục polling job đã tạo theo slot/body/key; không bắt tải lại ảnh cho job đã có; không tạo job trùng |
| TC-WEB-OUTFIT-10 | Cho áo xử lý thành công nhưng quần lỗi; thử lại quần | Báo lỗi thật, áo còn; không tạo điểm fit hay dữ liệu giả; chỉ xử lý lại món chưa thành công |
| TC-WEB-OUTFIT-11 | Chặn URL ảnh catalog hoặc CORS; thử file ảnh hỏng; từ chối camera | Lỗi thân thiện và có đường tải ảnh từ thiết bị; API vẫn validation file ảnh; không trắng trang |
| TC-WEB-OUTFIT-12 | Thử asset MHCLO có garment parent là human; thử GLB thiếu node garment | Garment con vẫn hiển thị khi loại body trùng bằng render layer; GLB không nhận diện được báo lỗi cấu trúc rõ ràng |
| TC-WEB-OUTFIT-13 | Tạo model mới sau khi đã mặc áo/quần | Xóa kết quả gắn với body cũ; giữ lựa chọn để xử lý lại theo body mới |
| TC-WEB-OUTFIT-14 | Mở ở 390px và desktop; dùng bàn phím, xoay/zoom; rời phòng thử khi đang xử lý | Layout không tràn ngang; nút có focus; camera dừng, polling client hủy, tài nguyên 3D được dọn; job server có thể tiếp tục |

Giới hạn cần kiểm tra cùng M2/M3: lớp ảnh nhận diện bằng prefix `Garment` đã đối chiếu pipeline hiện tại; lớp catalog nhận diện body theo tên mesh. Backend thay cấu trúc GLB phải cập nhật adapter; không đoán và ghép ngầm nếu không nhận diện được. Chưa có va chạm áo–quần, size thực tế hay GLB hợp nhất để tải cả bộ.
