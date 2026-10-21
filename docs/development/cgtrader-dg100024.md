# DG100024 — thử garment glTF bên ngoài

## Dữ liệu đã quan sát

ZIP do người dùng cung cấp: `data/external/cgtrader/GLTF.zip`, 346.040.269 byte.
Hai bản glTF Single Object và Multiple Objects, mỗi bản khoảng 734 MB do nhúng texture.
Bản Multiple Objects có 26 mesh, 5 material, không có skin; có skeleton/light không cần cho garment tĩnh.
Buffer hình học 12.432.904 byte, hai texture PNG 8192 × 8192.
Metadata được lưu ở `data/external/cgtrader/dg100024/inspection.json`.
Nguồn đã externalize ở `data/external/cgtrader/dg100024/source/`.
Read_Me ghi DigitalFashionWear, không cung cấp bằng chứng giấy phép cụ thể.

## Chuẩn bị để dùng

Từ thư mục gốc dự án, người dùng chạy bằng Blender đã cài:

```powershell
blender --background --python garment/external/prepare_gltf.py
```

Nếu `blender` chưa nằm trong PATH, thay bằng đường dẫn `blender.exe` trên máy,
dùng toán tử `&` của PowerShell trước đường dẫn có dấu cách.
Script đọc source externalized, giữ geometry/UV/material, resize texture tối đa 2048,
chỉ giữ cây Cloth và đóng gói GLB cùng báo cáo `.prepared.json` vào
`data/external/mpfb/dg100024/`. Không sửa ZIP gốc. Cần RAM để giải mã texture 8K.
Chỉ khi cả GLB và report xuất hiện thì catalog mới báo asset sẵn sàng.

Sau đó khởi động lại backend, tải lại trang, chọn
**Áo GLTF DG100024 — căn chỉnh thử**, size M và tạo body để mặc thử.
Nếu dùng `MPFB_ASSET_ROOT` riêng, chuyển thư mục `dg100024` đã chuẩn bị vào root đó.

## Khả năng và giới hạn

Catalog ID `cgtrader-dg100024`, engine `gltf_reference`;
API mode `reference_alignment`, kết quả method `blender_gltf_reference`.
Adapter nhập body GLB và garment, giữ chất liệu, căn theo chiều cao bằng một hệ số đồng đều.
Không cần native MPFB scene cho nhánh này. Report kết quả vẫn dùng hậu tố `.refit.json`
nhưng các trường mode/method phân biệt rõ với MPFB refit.

Đơn vị nguồn cm và chiều cao avatar tham chiếu 180 cm là cấu hình giả định công khai,
chưa được tác giả xác nhận. Source Y-up chuyển cm sang m khi đóng gói;
Blender importer đổi sang Z-up nội bộ rồi exporter xuất Y-up.
Trong catalog, `offset_m` là [X,Y,Z] theo trục Blender Z-up, `yaw_degrees` quay quanh Z.
Chỉ chỉnh các giá trị này sau khi kiểm tra hướng/độ cao trong viewer.

Tư thế tay nguồn giữ nguyên; chưa khớp pose body, chưa biến dạng theo vòng ngực/eo,
chưa xử lý xuyên da/che body, chưa mô phỏng vải hay tính fit score.
Size M chỉ là nhãn thử, chưa có size chart xác minh.
Geometry nguồn có accessor vượt 30.000 đỉnh; chưa tối ưu topology, chưa đạt xác nhận
ngân sách mesh cho triển khai thực tế. Script không tự giảm đỉnh làm hỏng chi tiết.

## Kiểm chứng

Chưa chạy script chuẩn bị bằng Blender, chưa render thử và chưa chạy test.
Không có số liệu kích thước GLB sau tối ưu hoặc xác nhận độ vừa.
Người dùng chạy và gửi log `GARMENT_PREPARED`, ảnh trước/ngang/sau và lỗi nếu có.

```powershell
python -m pytest tests/unit/garment/test_external_reference.py tests/unit/garment/test_mpfb_catalog.py
```

Kiểm tra: asset xuất hiện trong catalog; đổi chiều cao đổi tỷ lệ đồng đều;
chất liệu gốc vẫn hiện; report ghi `reference_alignment`, không ghi MPFB refit.
Nếu cần khớp theo số đo thực tế, bước tiếp theo là chuyển garment về pose chuẩn
và xây mapping/rig tương thích body, không dùng scale đồng đều làm tiêu chí nghiệm thu.
