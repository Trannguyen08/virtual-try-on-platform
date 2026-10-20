# M2 — Áo thun mẫu cho body-builder

Thời điểm: 2026-10-19 17:34:03, UTC+7 (Asia/Saigon).

## Vai trò và mục đích

M2, theo yêu cầu người dùng triển khai thử áo thun thay hình khối minh họa.
Có một điểm tích hợp tối thiểu trong script Blender của M1 để luồng hiện
tại gọi được generator M2. Không sửa dựng body MPFB hay luồng API mock.
Đã đọc `.git/HEAD`: nhánh hiện tại `feature/body`; không chạy Git hoặc đổi nhánh.

## File thực tế thêm/sửa

- Thêm `garment/mesh/tshirt_geometry.py`: trước chưa có; sau có
  `build_tshirt`, mesh quad nối liền thân/cổ/tay, bốn đường biên mở,
  lấy mẫu bán kính torso, khoảng hở tổng hợp theo size. Xóa các đỉnh
  không dùng tại khoảng mở nách trước khi trả mesh.
- Thêm `garment/mesh/blender_tshirt.py`: trước chưa có; sau có
  `create_tshirt`, đọc evaluated body vertices trong world space,
  BVH ray cast torso, suy hướng tay từ vertex cánh tay, tính lại normals,
  smooth shading và Solidify 1.5 mm hướng ra ngoài. Báo lỗi khi không
  lấy được torso/arm thay vì trả mesh thành công giả.
- Sửa `body/estimation/blender_body.py`, `make_clothing`: trước nhánh
  không có asset tạo áo từ ellipsoid; sau category `t_shirt` gọi M2,
  dùng size làm khoảng hở thay vì scale toàn bộ áo. Nhánh này return
  trước bước scale cũ. Asset GLB/OBJ vẫn được ưu tiên. Asset có material
  giữ material gốc thay vì bị xóa; asset trống material nhận màu dự phòng.
- Thêm `tests/unit/garment/test_tshirt_geometry.py`: TC-GAR-02 kiểm tra
  surface connected, bốn boundary loops, edge manifold, hữu hạn, giới hạn
  vertex, khoảng hở tổng hợp tăng theo size/cổ cố định, sampler lỗi rõ ràng.
  Các kiểm tra này chưa xác nhận GLB export, mô phỏng hay chart TC-GAR-04.
- Thêm `docs/report/evidence/garment/tshirt-template-check.md`: cách chạy
  test nhẹ, kiểm tra UI với job mới, điều kiện áp dụng và giới hạn đã biết.
- Thêm chính file log này.

## API, schema, đơn vị, database, asset

- Không sửa endpoint/schema/database. Đã đối chiếu consumer tại
  `backend/services/blender_body.py`: chỉ marker `CLOTHING_METHOD=asset`
  được gắn method asset; marker mới `synthetic_tshirt` vẫn đi nhánh
  `blender_illustrative_clothing`, source `mock`. Không gắn nhãn draping thật.
- Geometry dùng mét trong world space của Blender, Z-up nội bộ adapter;
  exporter hiện hữu `export_yup=True` chuyển GLB sang Y-up. Không dịch
  riêng gốc body hoặc garment. +Z forward sau export cần kiểm chứng trực quan.
- Không thêm package, weights, cache, ảnh hay binary asset vào repo.
- Nhánh asset ngoài giữ texture; hệ quả đã biết: swatch không tint các
  material có sẵn. Tô màu vẫn áp dụng cho áo tổng hợp và asset thiếu material.

## Ảnh hưởng và owner phối hợp

- M1: `make_clothing` có import vào M2; owner cần xác nhận trên body MPFB
  thật với nhiều tỷ lệ người. Không thay đổi `mpfb_body` hoặc `make_body`.
- M2: generator synthetic, không phải mesh theo chart, collision solver
  hay ảnh sản phẩm; chịu trách nhiệm chỉnh topology và fitting tiếp.
- M3: không thay job/source/schema; kiểm tra job lỗi và GLB export runtime
  chưa thực hiện. Handler hiện có sẽ biến lỗi generator thành job failed.
- M5: không sửa viewer; UI vẫn thông báo trang phục minh họa/source mock.
  Người dùng cần tạo job mới, chọn lớp Có trang phục. Luồng `/api/tryon`
  mock hình hộp không đổi trong đợt này.
- M4: không sửa fit/AI và không phát sinh fit score; tích hợp mesh này với
  pipeline đo Fit chưa kiểm tra.

## Xung đột và nguy cơ

- Đã xác nhận: thiếu asset ngoài thì trước đây tạo ellipsoid/cone; luồng
  mock backend riêng vẫn trả fixture hộp. Đợt này chỉ cải thiện body-builder
  cho áo thun, không tuyên bố mọi luồng thử đồ đã dùng mesh mới.
- Nguy cơ: tư thế tay khác mặc định, body quá khác tỷ lệ, vị trí cổ/vai
  gần đúng có thể gây xuyên hoặc áo không vừa. Chưa kiểm tra bằng render.
- Ray cast giả định tâm torso nằm trong thân; body không hợp lệ có thể
  gây job lỗi. Không dùng fallback hình hộp cho nhánh áo mẫu.
- Material asset ngoài giữ nguyên nên không bảo đảm swatch thay đổi màu
  asset. Cần thiết kế tint theo material nếu mở rộng bước sau.

## Kiểm thử và kết quả

Chưa chạy test (Chờ User xác nhận). Không chạy pytest, Blender, formatter,
package install, server hoặc Git theo Rule 01–02. Đã đọc code consumer và
rà soát nội dung patch; chưa có evidence PASS về hình học/runtime hay ảnh.

Lệnh người dùng chạy:

```powershell
python -m pytest tests/unit/garment/test_tshirt_geometry.py -q
```

## Bàn giao và việc còn lại

Người dùng/M1/M2: chạy unit test, tạo body mới + `demo-tshirt` size M,
chọn Có trang phục, xoay kiểm tra cổ/vai/nách/tay/gấu và lưu ảnh cùng
tham số body. Thử S/L và body gầy/đầy đặn theo checklist evidence.
Sau khi có kết quả mới điều chỉnh tỷ lệ vai/cổ/tay và collision; chưa
khẳng định mặc đẹp hoặc không xuyên trên mọi body. M3 kiểm tra GLB/job
runtime; M5 có thể bổ sung nhãn áo mẫu chi tiết ở đợt sau nếu cần.
