# M2 — Đặt áo tái dựng từ ảnh theo bề mặt body

## Mục đích và nguyên nhân

Ảnh polo đầu vào liền mạch nhưng mesh tái dựng chỉ có độ sâu khoảng ±0,026 m. Body dày hơn nhiều. Cách ghép cũ đẩy từng đỉnh theo pháp tuyến tam giác gần nhất, giới hạn 0,12 m; với job thực tế có 22.860/29.062 đỉnh bị đẩy và 8.911 đỉnh cần dịch trên 0,06 m. Ngưỡng cho `local_parametric` đã bị nới đến 40%, cho phép GLB có lỗ lớn và phần gấu áo chui vào vùng háng được phát hành.

## File thay đổi

- `garment/simulation/blender/compose_tryon.py`: trước đây dùng `fit_to_body` cho mọi áo và chấp nhận biến dạng lớn. Nay riêng áo tái dựng từ ảnh (`tshirt`, `shirt`, `jacket`, `dress`) chiếu mặt trước/sau theo tia chiều sâu lên body, giữ tọa độ ngang/cao, làm mượt chiều sâu theo cạnh mesh, giữ gấu áo dưới hông không đi theo khe giữa hai chân, gắn mép nối với hai tấm áo và kiểm tra lại tỷ lệ xuyên. Trả `placement=body_ray_projected_shell`; báo thêm số tia trúng/trượt. Garment khác giữ đường xử lý cũ với ngưỡng biến dạng 5%.
- `.agents/memory/ACTIVE_CONTEXT.md`: ghi nguyên nhân, thay đổi, kết quả kiểm tra và việc còn lại của đợt M2 này.
- File log này: mới; không có bản trước.

## Ảnh hưởng tích hợp

- API/schema/database: không đổi. Trường `placement` hiện có nhận giá trị mới; M3 cần biết giá trị này khi phân tích job. M3 tiếp tục nhận các trường báo cáo cũ; hai trường số tia bổ sung không được worker sử dụng.
- Đơn vị/hệ trục: GLB vẫn là mét, Y-up, +Z forward; phép chiếu thực hiện trong hệ Blender Z-up sau import, export về Y-up.
- Asset: các scene đã phát hành trước đây giữ nguyên; chỉ job mới dùng thuật toán mới. Không thêm asset nhị phân vào repo. Các file GLB/PNG kiểm tra tạm đã xóa.
- M1: dùng bề mặt body hiện có, không đổi mesh M1. M4: không đổi fit score. M5: viewer nhận GLB cùng hợp đồng, hình áo mới có ít vùng xuyên hơn.
- Xung đột: thay đổi M3/M5 chưa commit từ các đợt trước được giữ nguyên; đợt này chỉ sửa code M2. Rủi ro còn lại: mặt sau và hai bên vẫn suy từ một ảnh; đây là ghép hình học tĩnh, chưa phải mô phỏng vải. Kiểm tra tỷ lệ xuyên là lấy mẫu đỉnh, không chứng minh mọi tam giác hoàn toàn không giao nhau.

## Kiểm tra thực tế

- `pytest tests/unit/garment/test_compose_tryon.py --import-mode=importlib -q`: PASS 5/5. Lệnh pytest không có `--import-mode=importlib` bị lỗi thu thập module `garment.test_compose_tryon` do cách import của bộ test hiện tại.
- Blender 5.2.2 ghép cùng áo với body `2b8cfe9826124a049449fa6cad9c2ef2`: PASS, `penetration_fraction=0`, `severe_penetration_fraction=0`, xuất GLB; đã xem render trước/bên/sau, các lỗ lớn ở ngực và hông không còn.
- Blender ghép cùng áo với body `bf093dda7dab47c0a906ac4b64ca5ba3`: PASS, hai tỷ lệ trên bằng 0, xuất GLB.
- Chưa chạy lại toàn bộ luồng HTTP hoặc kiểm tra trực tiếp trong trình duyệt. Cần tạo job thử đồ mới để xem asset mới; lịch sử job cũ vẫn trỏ đến scene cũ.

## Bàn giao

M3/M5 kiểm tra lại job mới trong ứng dụng. Nếu cần áo rủ thật và mép tay/gấu mượt hơn, M2 cần mô phỏng vải đã hiệu chuẩn hoặc template 3D phù hợp kích cỡ; một ảnh chỉ cung cấp hình học mặt trước.
