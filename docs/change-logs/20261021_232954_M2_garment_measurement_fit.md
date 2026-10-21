# Change Impact Log — Garment fitting theo body và số đo (2026-10-21)

## Vai trò và mục đích

- Owner chính: M2 (Garment & Simulation).
- Phối hợp: M3 (API/schema/worker), M5 (giao diện thử đồ).
- Mục tiêu: cho phép tự căn garment theo số đo body hoặc nhập chu vi áo/quần cụ thể; xử lý hiện tượng vỏ áo phẳng bị body che/lệch form.

## File thay đổi

- `garment/simulation/blender/compose_tryon.py`: thêm `fit_garment_width_profile`; trước đây composer chỉ canh chiều cao/vị trí và chiếu sâu bề mặt. Nay profile ngang được scale theo từng vùng ngực/eo/gấu hoặc eo/mông trước bước chiếu bề mặt. Báo cáo placement chứa profile scale và chế độ fitting.
- `backend/schemas/image_tryon.py`: `ImageTryOnGarment` nhận `fit_mode`, `ease_cm`, `garment_measurements_cm`; validator bắt buộc ngực cho áo, eo+mông cho quần/váy, ngực+eo cho váy liền và chặn trường không phù hợp slot.
- `backend/workers/image_tryon.py`: đưa số đo body đã lưu và thiết lập fitting vào metadata M2. Ở chế độ nhập số đo, dùng chu vi ngực/eo làm reference khi hiệu chuẩn chiều dài ảnh. Bổ sung ánh xạ `BODY_MEASUREMENTS_MISSING` và `GARMENT_MEASUREMENT_MISMATCH` từ lỗi Blender thành lỗi job.
- `frontend/src/api/imageTryOnApi.ts`: thêm kiểu và serialize ba trường fitting vào `garments_json`.
- `frontend/src/pages/tryon/ImageTryOnPage.tsx`: thêm control tự căn/nhập số đo cho từng slot; ease chỉ gửi ở auto; có thông báo cho lỗi thiếu số đo body và scale không an toàn.
- `docs/api/api-contract.md`: ghi contract fitting và mô tả heuristic.
- `.agents/memory/ACTIVE_CONTEXT.md`: ghi lại thay đổi, đơn vị, nghiệm thu và giới hạn.

## Ảnh hưởng contract và hệ thống

- API: multipart `garments_json` có thêm `fit_mode` (`auto`/`measurements`), `ease_cm`, và chu vi garment theo cm. Mặc định `auto`; request cũ có thể dùng giá trị mặc định schema.
- Đơn vị: circumference/body measurements là cm ở contract; GLB và xử lý hình học giữ mét. Hệ trục giữ Y-up, +Z forward theo contract module.
- Database: không đổi schema/migration.
- Asset: GLB đầu ra giữ định dạng hiện tại. Job đã hoàn thành không được tái xử lý; cần tạo job mới.
- Module: M2 thay đổi geometry profile; M3 truyền dữ liệu/validation/error mapping; M5 cung cấp UI.

## Giới hạn và rủi ro

- Bề rộng mặt trước được ước lượng bằng `0.40 × chu vi / bề rộng ảnh hiện tại`, dựa trên giả định tiết diện oval và ảnh garment 2D. Đây là heuristic tham khảo, không phải dựng rập hoặc mô phỏng vải.
- Mesh vẫn là shell tĩnh được chiếu ra ngoài bề mặt body với clearance 1 cm; không dựng hoàn chỉnh mặt sau/tay áo, nếp gấp hay độ rủ vật lý.
- Auto cần body record đã lưu đủ ngực+eo cho upper/onepiece hoặc eo+mông cho lower. Body cũ thiếu measurements cần cập nhật/lưu lại hoặc chọn nhập chu vi garment thủ công.
- Scale nằm ngoài 0.65–1.5 bị từ chối để tránh biến dạng quá mức; UI hiển thị mã lỗi có hướng dẫn.
- Chưa kiểm tra bằng Blender thật để xác nhận độ ổn định của profile trên các ảnh/body đa dạng.

## Kiểm tra

- Chưa chạy test, build frontend, Blender hoặc server; theo yêu cầu không tự chạy kiểm thử.
- Đã rà soát tĩnh đường truyền schema → worker metadata → composer và frontend multipart payload.

## Bàn giao

- Khởi động lại backend, image try-on worker và frontend; tạo job mới với auto hoặc measurements để nghiệm thu end-to-end.
- Nếu body chưa có số đo cm, cập nhật body rồi thử chế độ auto.
