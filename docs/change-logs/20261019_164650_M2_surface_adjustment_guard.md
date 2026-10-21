# Change Impact Log — M2: sửa ngưỡng kiểm tra biến dạng khi ghép đồ

## Vai trò và mục đích

- **Role:** M2 Garment & Simulation.
- **Mục đích:** Sửa điều kiện từ chối quá rộng làm job quần có các chỉnh sửa bề mặt nhỏ bị báo `SEVERE_MESH_PENETRATION`.

## File thay đổi

| File | Trước → sau |
| --- | --- |
| `garment/simulation/blender/compose_tryon.py` | `fit_to_body()` chỉ trả số đỉnh đã chỉnh và số đỉnh cần đẩy quá 12 cm → trả thêm số đỉnh cần đẩy hơn 6 cm. `validate_surface_adjustment()` từ chối khi hơn 35% đỉnh được chỉnh bất kể độ dịch chuyển → chỉ từ chối khi hơn 5% đỉnh cần dịch trên 6 cm. `TRYON_REPORT` bổ sung `large_adjustment_vertices`. |
| `tests/unit/garment/test_compose_tryon.py` | Hai test ngưỡng cũ dựa vào tổng số đỉnh đã chỉnh → kiểm tra dữ liệu hồi quy: 3.811/53.972 đỉnh cần chỉnh mạnh bị từ chối; 204/54.016 đỉnh cần chỉnh mạnh được chấp nhận. |

## Ảnh hưởng và owner

- **API/schema/database:** Không sửa route, schema, bảng hoặc trạng thái job. `TRYON_REPORT` nội bộ có thêm một khóa; worker M3 chỉ đọc các khóa cũ nên không cần đổi consumer. Job mới với hình học tương tự quần 70 cm có thể hoàn tất thay vì `failed`.
- **Đơn vị/hệ trục:** Ngưỡng 6 cm được tính bằng `0.06` mét trong Blender. GLB vẫn Y-up, +Z forward khi xuất.
- **Asset:** Không ghi đè asset đã đăng ký. Các GLB chẩn đoán và kiểm tra nằm dưới `data/outputs/validation/` (gitignored); job đã `failed` không tự chạy lại.
- **Module khác:** M3 tiếp tục gọi cùng script và đọc cùng report; M5 hiển thị GLB từ asset URL như cũ. Không sửa M1, M3, M4, M5. Owner M3/M5 cần xác nhận nếu muốn thay đổi thông báo lỗi hoặc trải nghiệm chạy lại job.

## Bằng chứng, xung đột và rủi ro

- Hai job dùng body `062226321c79436a80a0b60428faaccc`. Job `itry_a9722cbe7195486d95687544f558c015` chọn `tshirt` nhưng ảnh xem trước là quần jeans; cần chọn đúng loại trang phục. Nó có 3.811/53.972 đỉnh cần dịch hơn 6 cm nên vẫn bị chặn.
- Job `itry_1ae686087dec411eb38bbe2ee7a390d3` chọn `pants`, 70 cm: 29.298/54.016 đỉnh được chỉnh nhưng chỉ 204 đỉnh cần dịch hơn 6 cm. Ngưỡng cũ chặn nhầm trường hợp này. Sau sửa, GLB được xuất, phần đỉnh còn xuyên body là 0,003639 theo phép đo hiện tại, phần xuyên sâu là 0.
- **Xung đột đã xác nhận:** Chọn `tshirt` cho ảnh jeans tạo mesh loại sai. M2 chưa triển khai bộ nhận diện loại ảnh tự động; người dùng cần chọn `pants`.
- **Rủi ro:** Kiểm tra biến dạng vẫn là ngưỡng hình học kinh nghiệm; single-image reconstruction có thể tạo vùng đáy/quần chưa giống đồ thật. Hình chiếu trước/bên đã xem nhưng chưa nghiệm thu trong Three.js viewer. Không suy ra số đo thật hoặc fit score từ kiểm tra này.

## Kiểm tra và bàn giao

- `pytest tests/unit/garment/test_compose_tryon.py -q`: **5 passed**. Có cảnh báo deprecation từ Starlette/TestClient không liên quan.
- Chạy Blender trên đúng hai input lỗi: job chọn `tshirt` không xuất GLB và báo `SEVERE_MESH_PENETRATION`; job chọn `pants` xuất GLB với `large_adjustment_vertices=204`, `deep_vertices=0`, `penetration_fraction=0.003639`.
- `GlbValidator` trên GLB quần: hợp lệ, 9.853.268 byte, 4 mesh, 4 material, 3 texture, có PBR.
- Việc còn lại: tạo job mới với `pants` và chiều dài quần đo thực tế để kiểm tra trong viewer. Hai job lỗi cũ vẫn ở trạng thái `failed`; chưa thay đổi dữ liệu DB để chạy lại.
