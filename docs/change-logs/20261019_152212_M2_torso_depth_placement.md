# Change Impact Log — M2: căn chiều sâu trang phục theo thân người

## Vai trò và mục đích

- **Role:** M2 Garment & Simulation.
- **Mục đích:** Sửa cảnh thử đồ tĩnh đặt áo/quần lệch ra phía trước body do lấy tâm chiều sâu từ hộp bao toàn thân (bao gồm đầu/mặt và mông).

## File thay đổi

| File | Trước → sau |
| --- | --- |
| `garment/simulation/blender/compose_tryon.py` | `main()` dùng trung điểm chiều sâu của toàn body → dùng `torso_depth_center()` lấy trung vị tâm các lát cắt ngực hoặc hông; thêm `body_vertices()` đọc đỉnh body đã áp modifier. `validate_surface_adjustment()` từ chối mesh phải đẩy hơn 35% số đỉnh để tránh xuất cảnh quần bị kéo giãn. |
| `tests/unit/garment/test_compose_tryon.py` | Chưa tồn tại → thêm 5 test TC-GAR-05 cho áo, quần, body thiếu vùng thân và giới hạn biến dạng. |

## Ảnh hưởng

- **API/schema/database:** Không thay đổi route, JSON contract, bảng dữ liệu hoặc hàng đợi. Worker M3 tiếp tục gọi cùng script Blender. Job có garment quá nhỏ nay có thể chuyển `failed` với mã sẵn có `SEVERE_MESH_PENETRATION` thay vì trả GLB sai hình; M5 đã hiển thị `error.code` và `error.message` khi job failed.
- **Đơn vị và hệ trục:** Tính trong khung native Blender sau khi import GLB; các khoảng cách dùng mét. GLB đầu vào/đầu ra vẫn Y-up, +Z forward. Không đổi phép quy đổi cm tại API.
- **Asset/dữ liệu:** Không sửa asset gốc hoặc job đã hoàn tất. Job mới sẽ tạo scene GLB với vị trí khác. Các GLB/PNG thử nghiệm nằm trong `data/outputs/validation/` (thư mục output không commit), không phải asset phục vụ qua API.
- **File kiểm tra được tạo:** `data/outputs/validation/pants-length-100cm-validation.glb`, `tryon-placement-after.glb`, `tryon-placement-100cm.glb`, `tryon-shirt-after.glb`, `tryon-guard-100cm.glb`, `tryon-guard-shirt.glb`, `tryon-placement-compare.png`, `tryon-100cm-compare.png` (các tên sau cùng thuộc cùng thư mục). Đã thử dọn các bản trung gian, nhưng automatic approval review chặn lệnh xóa với thông báo `blocked by policy`; toàn bộ file vẫn còn.
- **Module liên quan:** M1 cung cấp body MPFB; M3 gọi composer và đăng ký GLB; M5 tải scene theo URL cũ. Không đổi mã các module đó. Hình ảnh hiển thị cuối cần M5/người vận hành xác nhận thủ công.

## Bằng chứng, xung đột và rủi ro

- Trên body 1,8 m của job đã kiểm tra, tâm hộp bao toàn thân là 0,143 m theo chiều sâu; tâm lát cắt hông là 0,022 m và tâm lát cắt ngực là 0,033 m. Phép căn cũ đặt trang phục lệch về trước khoảng 0,11–0,12 m.
- Job quần đã kiểm tra dùng `garment_length=70 cm`; khoảng 29.298/54.016 đỉnh (54%) phải đẩy khỏi body sau khi căn, tạo biến dạng lớn. Job này nay bị từ chối thay vì âm thầm kéo giãn. Gấu quần cao cũng là hệ quả của số đo nhập, không được tự kéo dài trong composer.
- Bản thử scale mô hình lên 100 cm chỉ để kiểm tra hành vi với kích thước tương thích hơn, không xác nhận quần thật dài 100 cm hoặc khuyến nghị nhập sai số đo. Bản này cần đẩy 4.209/54.016 đỉnh (8%), xuất GLB với `penetration_fraction=0`.
- Rủi ro còn lại: mesh parametric từ một ảnh chưa có draping/rigging; chưa kiểm tra GLB mới trong viewer. Không tuyên bố khớp hoàn toàn với mọi body/ảnh.

## Kiểm thử và bàn giao

- **PASS:** `TC-GAR-05` (5 unit tests), lệnh `.\.venv\Scripts\python.exe -m pytest tests/unit/garment/test_compose_tryon.py -q` cho kết quả `5 passed`; có một cảnh báo deprecation từ Starlette/TestClient không liên quan.
- **Blender kiểm tra:** Với body MPFB 1,8 m và quần 70 cm, composer không xuất GLB và ghi `SEVERE_MESH_PENETRATION`. Với bản scale thử 100 cm, composer xuất GLB, `penetration_fraction=0`, `deep_vertices=0`. Áo 80 cm cũng xuất GLB, `penetration_fraction=0`, `deep_vertices=0`. Đã xem hình chiếu điểm 3D trước/sau tại `data/outputs/validation/`.
- **GLB validator:** Hai cảnh thử quần 100 cm và áo 80 cm đều hợp lệ, có 4 mesh, 4 material, 3 texture và PBR; lần lượt 128.706 và 81.570 triangle.
- **Chưa chạy:** Tạo job mới qua API và xem GLB mới trong viewer. Cần người vận hành xác nhận ảnh mặt trước/mặt bên để nghiệm thu trực quan.
- **Bàn giao:** Người vận hành tạo job mới với số đo chiều dài thật và chụp mặt trước/mặt bên; M2 đánh giá phần mesh/draping còn lệch nếu có. M3/M5 chỉ cần xem lại nếu API hoặc viewer hiển thị scene khác GLB mới.
