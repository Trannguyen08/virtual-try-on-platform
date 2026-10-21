# M2 — Kéo gấu áo từ lát cắt hông/eo

Thời điểm: 2026-10-19 18:02:26 UTC+7 (Asia/Saigon).

## Vai trò, mục đích và bằng chứng

M2 xử lý lỗi user cung cấp: `ValueError: Cannot sample a continuous torso
for T-shirt`. Log xác nhận một mẫu bán kính thiếu/không hợp lệ; log cũ
chưa chỉ vị trí nên chưa xác nhận chính xác mẫu lỗi trên body thật.
Đã phát hiện giả định sai trong code: mọi lát cắt kể cả gấu tại 46% và
49% chiều cao đều phải chạm body ở đủ 32 hướng. Vùng gần hai chân không
bảo đảm lát cắt kín quanh tâm thân. Đây là lỗi thuật toán garment, không
phải bằng chứng body M1 sai contract hoặc thiếu MPFB.

## File thực tế sửa và trước → sau

- `garment/mesh/tshirt_geometry.py`, `build_tshirt`: trước lấy mẫu mọi
  ring độc lập, thiếu một hướng sẽ lỗi chung. Sau lấy các profile từ 53%
  trở lên; chọn profile kín thấp nhất trong 53%, 57%, 61% làm hông/eo
  tham chiếu. Các ring thấp hơn dùng cùng profile đó, giữ độ cao gấu và
  khoảng hở theo size; không quấn riêng hai chân hoặc tạo ellipse giả.
  Không có anchor thì báo lỗi rõ. Profile thân trên lỗi ghi level và
  angular sample, không âm thầm dùng anchor cho toàn bộ thân.
- `garment/mesh/blender_tshirt.py`, `create_tshirt`: thêm marker
  `TSHIRT_HEM_METHOD=measured_hip_profile_extension` khi tạo geometry thành công.
- `tests/unit/garment/test_tshirt_geometry.py`: thêm TC-GAR-02 hồi quy
  khe chân, ba mức anchor, gấu giữ vị trí/độ rộng đo được, và thân trên
  thiếu mẫu vẫn lỗi. Giữ các bài topology/size/invalid sampler hiện có.
- `docs/report/evidence/garment/tshirt-template-check.md`: giải thích cách
  kéo gấu và giới hạn fallback. Không sửa trạng thái test thành PASS.
- Thêm file log này.

## API/schema, đơn vị, database, asset và module

Không sửa API/schema/database/catalog hoặc binary asset. Metres và khung
world Blender Z-up được giữ; export Y-up vẫn ở script hiện hữu.
M1 body không bị sửa. M3 nhận job thành công/lỗi theo contract cũ; lỗi
geometry mới có mức lấy mẫu rõ hơn trong log. M5 viewer không đổi; phải
tạo job áo mới để có geometry mới. M4 Fit/AI không thay đổi, chưa kiểm tra
mesh này cho metrics. Nguồn áo vẫn synthetic/mock, không phải cloth simulation.

## Xung đột/nguy cơ và owner phối hợp

Giả định gấu phải trùng bề mặt body là lỗi đã xác nhận qua code. Việc nó
có phải vị trí gây lỗi trên body user hay không cần lần chạy mới xác nhận.
Nếu không tìm được hông/eo kín hoặc thân trên thiếu mẫu, job vẫn failed với
diagnostic rõ hơn. Vai/tay/cổ và khả năng xuyên body vẫn chưa render kiểm chứng.
Owner M2 kiểm tra hình dáng; M1 hỗ trợ body parameters; M3 nhận log nếu lỗi.

## Kiểm thử và bàn giao

Chưa chạy test (Chờ User xác nhận). Không chạy pytest/Blender/Git.
Lệnh người dùng chạy từ root:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/garment/test_tshirt_geometry.py -q
```

Khởi động lại backend, tạo body/job mới và chọn áo Minimalist Signature
size M rồi xem lớp Có trang phục. Gửi ảnh render hoặc dòng exception mới
nếu còn lỗi. Chưa khẳng định đã xuất GLB thành công trên body thực tế.
