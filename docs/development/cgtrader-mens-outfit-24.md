# Men’s Outfit 24 — tình trạng nhập asset

Trạng thái: **đã giải nén nguồn, chưa có mesh quần áo dùng được trong pipeline**.
Chưa đăng ký vào catalog và chưa tạo GLB mặc thử.

## File đã nhận

ZIP người dùng cung cấp:
`data/external/cgtrader/Resource+and+Project+Files+-+Men-s+Outfit+24.zip`
(168.729.396 byte).

Đã giải nén 26 file vào `data/external/cgtrader/mens-outfit-24/source/`,
giữ cấu trúc thư mục và không ghi đè file đã có. Bỏ `desktop.ini`.

| Nhóm | Nội dung |
| --- | --- |
| Project trang phục | `ZPRJ/A Pose.zprj` — 94.958.745 byte |
| Preview | `ZPRJ/A Pose.png` |
| Avatar FBX | `Avatar/Male/Male Stand + Animate + Posed + A.fbx` |
| Auto-fitting avatar | `Auto-fitting/Auto-fitting - Male.avt` |
| Hình ảnh | 14 PNG, 9 JPG, bao gồm preview và texture |

Preview hiển thị áo khoác đen, áo thun trắng và quần cargo. FBX nằm trong
thư mục Avatar; kiểm tra chuỗi tên node trong binary thấy Genesis8Male và
Genesis8MaleEyelashes. Chưa import/render FBX để nghiệm thu; không coi file
avatar này là mesh trang phục cần mặc lên body MPFB.

ZIP không có `.obj`, `.glb`, `.gltf`, `.mhclo`, `.mtl` hoặc `.mhmat`.
File ZPRJ bắt đầu bằng header ` ZPRJ ... CLO `; không phải ZIP/OBJ có thể
đổi đuôi rồi đưa vào importer hiện tại.

User xác nhận máy chưa cài CLO 3D hoặc Marvelous Designer. Chưa có bộ
chuyển đổi ZPRJ được kiểm chứng cho pipeline này; không cài phần mềm hoặc
addon chuyển đổi ngoài để thử trên máy người dùng.

## Cần gì để tiếp tục

Ưu tiên lấy bản export **GLB có mesh quần áo và texture đóng gói** của chính
bộ này, hoặc **OBJ + MTL + texture**; FBX quần áo cũng có thể chuẩn bị trong
Blender. File FBX phải chứa quần áo, không chỉ avatar đi kèm.

Kiểm tra trang tải của tác giả xem có mục OBJ/FBX/GLB riêng bên cạnh
Resource and Project Files. Nếu chỉ có ZPRJ, cần mở bằng phần mềm hỗ trợ
và export garment. Hướng dẫn chính thức CLO:
[3D File (OBJ) Import/Export](https://support.clo3d.com/hc/en-us/articles/115000494107-3D-File-OBJ-Import-Export).

Khi export:

- Chỉ chọn quần áo, không xuất avatar; giữ riêng từng món nếu có thể.
- Giữ UV/material/texture và tư thế A tương ứng.
- Với OBJ/FBX, ghi lại đơn vị và hướng trục. Không đoán tỷ lệ từ tên file.
- GLB theo chuẩn mét/Y-up; vẫn cần kiểm tra gốc, tư thế và hướng mặc.

Đặt file mới vào `data/external/cgtrader/mens-outfit-24/export/`.
Sau khi có mesh, mới kiểm tra topology, căn body, chuẩn bị mapping/deformation
và đăng ký catalog. Có mesh đã export chưa có nghĩa tự refit chính xác.

## Phạm vi và nguồn

File này khác mẫu Men T-shirt set-free đã gợi ý trước. Chưa có URL trang
sản phẩm hoặc giấy phép kèm ZIP; không gắn lại tên tác giả/CC0/giấy phép
của mẫu khác. Cần lưu nguồn và giấy phép đúng asset khi đăng ký sử dụng.

Nguồn giải nén và ZIP đều nằm trong `data/external/` đã gitignore, không
đưa asset nặng vào Git. Không sửa API, viewer hoặc catalog ở đợt này.
