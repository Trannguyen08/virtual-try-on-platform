# M2 — Khoảng hở vùng vai áo

Thời điểm: 2026-10-19 18:10:33 UTC+7 (Asia/Saigon).

## Vai trò và mục đích

M2 sửa theo phản hồi user: áo đã hiện nhưng hơi lộ phần vai trên. Đây là
bằng chứng user về render thành công sau đợt trước, chưa có ảnh/thông số
để xác định mức xuyên. Qua code, shoulder bridge được nội suy từ vai tới
cổ theo tỷ lệ, chưa bảo đảm cao hơn bề mặt vai body.

## File thêm/sửa, trước → sau

- `garment/mesh/torso_sections.py`: thêm `surface_height` tìm giao thẳng
  đứng cao nhất trên các tam giác trong dải độ cao; cache triangle candidates
  theo band, kiểm tra bbox XY và barycentric. Không dùng điểm trên đầu hoặc
  thân dưới nằm ngoài band; thiếu giao trả None.
- `garment/mesh/tshirt_geometry.py`, `build_tshirt`: thêm callback tùy chọn
  `sample_shoulder_height`; `lift_shoulder` nâng ring vai trên và các ring
  trung gian nối cổ lên ít nhất mặt body + 0.006 * height / 1.7 mét. Trước
  chỉ nội suy tỷ lệ; sau giữ cao độ cũ nếu đã cao hơn. Không sửa ring cổ
  cuối hoặc gấu; sleeve attachment dùng boundary vai sau khi nâng.
- `garment/mesh/blender_tshirt.py`: nối callback surface sampling trong
  dải floor + 0.74h đến floor + 0.87h vào generator hiện hữu.
- `tests/unit/garment/test_torso_sections.py`: TC-GAR-02 thêm mặt vai dốc,
  mặt đầu/body dưới ngoài band và tọa độ nằm ngoài triangle.
- `tests/unit/garment/test_tshirt_geometry.py`: TC-GAR-02 hồi quy clearance
  vai, connectivity faces giữ nguyên, gấu/cổ cuối không thay đổi.
- `docs/report/evidence/garment/tshirt-template-check.md`: thêm mô tả
  correction ở vai, khoảng hở và giới hạn face interpolation.
- Thêm file log này.

## Ảnh hưởng API/schema, đơn vị, database, asset và module

Không sửa API/schema/database/source/material hoặc binary asset. Body M1
không bị đổi; geometry vẫn world-space mét/Z-up Blender và exporter Y-up
hiện hữu. Chỉ áo thun synthetic được chỉnh. M3 dùng handler/job/GLB như
cũ; M5 xem job mới. M4 chưa kiểm tra correction này cho fit metrics.

## Xung đột/nguy cơ và owner phối hợp

Đã xác nhận thiếu ràng buộc mặt vai trong code. Chưa có ảnh để xác định
vai lộ do vertex hay mặt giữa vertex; correction không phải cloth collision
solver. Vùng sát cổ/tư thế khác và mặt nội suy vẫn có thể xuyên body;
cần kiểm tra ảnh trước/sau/bên. M2 chịu trách nhiệm hình dáng, M1 hỗ trợ
body parameters nếu tỷ lệ bất thường. Không cần đổi consumer M3/M5.

## Kiểm thử và bàn giao

User xác nhận áo đã render ở bản trước; bản correction mới chưa chạy test
(Chờ User xác nhận), chưa chạy Blender. Không Git/install.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/garment/test_tshirt_geometry.py tests/unit/garment/test_torso_sections.py -q
```

Khởi động lại backend, tạo áo/job mới và xem vai từ trước/sau/trên. GLB cũ
không tự cập nhật. Cần ảnh vùng còn lộ nếu phải tinh chỉnh tiếp; chưa tuyên
bố hết xuyên người trên mọi body.
