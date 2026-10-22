# M2 — Thay lấy mẫu tia từ tâm cố định bằng đường bao lát cắt

Thời điểm: 2026-10-19 18:06:16 UTC+7 (Asia/Saigon).

## Vai trò, mục đích và bằng chứng

M2 tiếp tục sửa áo mẫu theo log user: không tìm được profile kín tại
0.53–0.61 chiều cao. Bản kéo gấu trước đó chưa giải quyết lỗi thực tế.
Log xác nhận giả định mọi tia từ tâm bbox đều cắt được torso không đáp
ứng body này; chưa có bằng chứng khẳng định body M1 hỏng hoặc thiếu MPFB.
Đợt này thay thuật toán lấy mẫu, không tiếp tục dịch mức gấu theo phỏng đoán.

## File thực tế thêm/sửa

- Thêm `garment/mesh/torso_sections.py`: `TorsoSections` cắt tam giác với
  mặt phẳng ngang, gom đoạn cắt thành component theo tọa độ lượng tử hóa,
  chọn component trung tâm có diện tích convex hull lớn nhất. Dùng centroid
  diện tích làm tâm riêng từng lát cắt; tính bán kính qua giao đoạn 2D.
  `convex_hull`/`signed_area` không cần dependency ngoài stdlib.
  Không tìm thấy đường bao trung tâm thì trả thiếu dữ liệu/lỗi rõ.
- Sửa `garment/mesh/blender_tshirt.py`: trước tạo BVH và bắn tia từ tâm
  bbox cố định; sau cập nhật view layer trước evaluated mesh, dùng
  `calc_loop_triangles`, adapter `TorsoSections`, tìm anchor tại 53/57/61%
  rồi truyền sampler/tâm theo độ cao. Marker mới
  `TSHIRT_PROFILE_METHOD=triangle_section_convex_envelope`.
  Lỗi không có mặt cắt ghi chiều cao, số vertex/triangle để chẩn đoán.
- Sửa `garment/mesh/tshirt_geometry.py`: thêm tham số tùy chọn
  `sample_center`, dùng tâm từng ring; gấu dùng tâm của anchor, upper
  chest/back dùng tâm lát cắt tương ứng. Caller cũ không truyền tham số
  vẫn dùng tâm cũ. Cổ/vai/tay vẫn theo mẫu tỷ lệ và hướng tay hiện hữu.
- Thêm `tests/unit/garment/test_torso_sections.py`: TC-GAR-02 cho thân
  hộp lệch theo Y, hai arm component riêng, chỉ có vertices ở hai đầu
  chiều cao, kiểm tra tâm/bán kính 32 hướng, tích hợp dựng áo quanh thân
  lệch và mặt cắt ngoài body báo thiếu. Đây là fixture hình học giải tích,
  không thay cho kiểm tra body MPFB/render thật.
- Sửa `docs/report/evidence/garment/tshirt-template-check.md`: thay mô tả
  ray cast bằng triangle cuts, giải thích convex envelope và thêm lệnh test.
- Thêm file log này.

## API, schema, đơn vị, database, asset, module

Không sửa endpoint/schema/database/material/body generation hoặc binary asset.
Geometry tiếp tục mét trong Blender Z-up, exporter Y-up giữ nguyên. Không
dịch body; garment dùng world coordinates từ body hiện hữu. Convex hull
là envelope áo, không phải silent fix topology body hoặc mesh đo Fit.
Nguồn vẫn synthetic/mock; không có cloth simulation/fit score.
M1 cung cấp body; M3 tiếp tục bắt exception bằng handler hiện hữu; M5
không đổi consumer; M4 chưa kiểm tra envelope này cho fit metrics.

## Xung đột/nguy cơ và owner

Đã xác nhận patch trước vẫn thất bại qua log user. Tâm bbox cố định là
một giả định không cần thiết được loại bỏ. Chưa xác định yếu tố cụ thể
(độ lệch tâm, topology, transforms) gây tia hụt trong mesh MPFB thực tế.
Convex hull sẽ bắc qua chỗ lõm; nếu tay nối liền torso tại cùng độ cao,
có thể làm đường bao rộng. Vùng cổ/vai/tay vẫn cần kiểm tra xuyên body.
M2 chịu trách nhiệm đường bao/topology; M1 hỗ trợ tư thế và thông số body;
M3 hỗ trợ diagnostic nếu không tìm được mặt cắt. Không khẳng định hết lỗi.

## Kiểm thử và bàn giao

Chưa chạy test (Chờ User xác nhận), chưa chạy Blender, không Git/install.
Đã rà soát patch, công thức giao tia–đoạn và truyền tâm giữa adapter/generator.
Lệnh đề xuất từ root:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/garment/test_tshirt_geometry.py tests/unit/garment/test_torso_sections.py -q
```

Khởi động lại backend, tạo lại body và áo Minimalist Signature size M;
chọn Có trang phục, kiểm tra trước/sau/bên. Cần ảnh render hoặc log mới
để xác nhận GLB thành công và đánh giá hình dáng trên body thật.
