# M2 — Kiểm tra ZIP Men’s Outfit 24

Thời điểm: 2026-10-19 18:51:46 UTC+7 (Asia/Saigon).

## Vai trò và mục đích

M2 tiếp tục yêu cầu đưa trang phục CGTrader do user tải vào project để mặc
thử. Đã áp dụng skill m2-garment-expert và change-impact-log.

## Bằng chứng và kết quả

- Đã nhận `Resource+and+Project+Files+-+Men-s+Outfit+24.zip`, 168.729.396 byte.
- Liệt kê nội dung ZIP: project ZPRJ, avatar FBX/AVT, texture và preview;
  không có OBJ, GLB, GLTF hoặc MHCLO garment.
- Đọc header ZPRJ thấy ` ZPRJ ... CLO `; không phải archive ZIP nội bộ
  có mesh exchange để lấy ra bằng bộ đọc ZIP chuẩn.
- Kiểm tra chuỗi node FBX thấy Genesis8Male/Genesis8MaleEyelashes; FBX nằm
  trong thư mục Avatar. Không chạy Blender hoặc giả định FBX là garment.
- Xem preview A Pose.png: bộ áo khoác đen + áo thun trắng + quần cargo.
- User đã xác nhận chưa cài CLO 3D/Marvelous Designer. Hiện chưa có cách
  export ZPRJ được kiểm chứng trong môi trường này.

## File thực tế thêm/sửa

- Thêm 26 file nguồn giải nén dưới
  `data/external/cgtrader/mens-outfit-24/source/`: 1 ZPRJ, 1 AVT, 1 FBX,
  14 PNG và 9 JPG. Giữ thư mục Auto-fitting, Avatar/Male, Materials và ZPRJ;
  bỏ desktop.ini. Không sửa ZIP gốc, không ghi đè file có sẵn.
- Thêm `docs/development/cgtrader-mens-outfit-24.md`: inventory, trạng thái
  chưa import garment, yêu cầu export và bước tiếp tục.
- Thêm chính file log này. Không sửa code/config/contract khác.

## API, schema, đơn vị, database, asset và module

- API/schema/database/catalog/viewer không đổi. Chưa phát URL garment,
  chưa thêm sản phẩm giả có trạng thái ready.
- Chưa chuyển đơn vị/trục hoặc hình học; chưa có GLB đầu ra. Không đưa
  avatar Genesis8 vào thay body MPFB của user.
- ZIP gốc và ZPRJ nguồn >50 MB nằm trong data/external đã gitignore.
  Không Git/add/commit hoặc tải weights/dataset.
- Chưa xác định URL và giấy phép của đúng bộ này; không kế thừa metadata
  từ mẫu Men T-shirt set-free được gợi ý trước đó.

## Xung đột/nguy cơ và owner phối hợp

Đã xác nhận thiếu mesh garment ở định dạng pipeline hỗ trợ; có project
CLO không đồng nghĩa có OBJ/GLB sẵn. M1/M3/M5 không cần sửa để che lỗi định
dạng; M2 cần bản export garment để kiểm tra topology/material và fitting.
Các texture hiện có không đủ tái dựng hình học bộ đồ từ ảnh preview.

## Kiểm thử và trạng thái bàn giao

Đã kiểm tra inventory/header, đọc tên node FBX và xem preview; đã giải nén
nguồn bằng thao tác file I/O. Chưa chạy test/Blender/CLO, chưa có kết quả
mặc thử hoặc fitting PASS. Không cài phần mềm/Git hoặc sửa môi trường.

User cần lấy thêm bản export GLB hoặc OBJ+MTL+texture/FBX **quần áo** từ
trang tải/tác giả, đặt vào `data/external/cgtrader/mens-outfit-24/export/`.
Nếu chỉ có ZPRJ, cần phần mềm hỗ trợ mở và export garment trước khi M2
có thể tích hợp. Việc mặc bộ này lên body vẫn chưa hoàn thành.
