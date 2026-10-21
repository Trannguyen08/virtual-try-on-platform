# M2 — Căn áo và quần tái dựng từ ảnh lên body

## Nguyên nhân và mục tiêu

Phản hồi thực tế cho thấy áo polo còn thấp ở vai/tay, còn quần cần được kiểm tra riêng. Thuật toán cũ chỉ chiếu chiều sâu cho áo, quần vẫn đẩy từng đỉnh theo pháp tuyến gần nhất. Ngoài ra, bộ tạo mesh coi một phần cạnh bên gần gấu/cạp/ống tay là lỗ mở, nên các mép mặt trước và mặt sau không được nối. Một ảnh mặt trước chỉ có một số đo chuẩn tỷ lệ không cung cấp chính xác hình học tay áo, mặt sau hoặc độ rộng thực của quần; đợt sửa này chỉ cải thiện phép ghép hình học tĩnh.

## File thay đổi

- `garment/reconstruction/mesh_builder.py`: `_opening_name` nay chỉ đánh dấu cạnh ngang của cạp/gấu/ống quần là lỗ mở và thu hẹp cửa ống tay về đầu tay. Các cạnh dọc sát gấu và tay được nối trước/sau. Dựng lại ảnh thử: áo có đỉnh lỗ gấu từ 121 xuống 84, cuff phải/trái từ 53/46 xuống 17/14; quần có cạp từ 196 xuống 141 và hai gấu từ 117/132 xuống 57/61. Số đỉnh lỗ mở giảm vì cạnh bên không còn bị tính vào lỗ.
- `garment/simulation/blender/compose_tryon.py`: `fit_parametric_shell` dùng cho quần tái dựng từ ảnh ngoài các loại áo đã hỗ trợ. Thêm `lift_top_shoulders` nâng có kiểm soát vùng vai/tay theo hình biên trên, giữ vị trí cổ và gấu áo; giá trị lớn nhất được ghi trong `TRYON_REPORT`. Mức anchor toàn áo vẫn 0,84 chiều cao body; không thay đổi chiều dài áo do user khai báo. Vá lại docstring kiểm tra fallback.
- `tests/unit/garment/test_mesh_openings.py`: mới, 2 test `TC-GAR-02` cho cạnh ngang mở và cạnh dọc nối kín ở áo/quần.
- `.agents/memory/ACTIVE_CONTEXT.md`: ghi trạng thái và giới hạn của đợt này.
- File change log này: mới.

## Tác động tích hợp và giới hạn

- API/schema/database: không đổi. `placement` của quần ảnh có thể là `body_ray_projected_shell` thay vì `body_height_anchor_and_surface_clearance`; M3/M5 đang dùng trường chuỗi. `TRYON_REPORT` thêm `shoulder_lift_max_m`; worker không dùng trường mới.
- Đơn vị/hệ trục: tọa độ nội bộ mét, Blender Z-up sau import và GLB Y-up khi export; số đo bên ngoài vẫn cm. Không âm thầm rút ngắn áo 70 cm hoặc quần 80 cm để nhìn vừa hơn.
- Ảnh hưởng M1: chỉ đọc body mesh hiện có. M3: job mới tạo scene mới; scene lịch sử giữ nguyên. M4: không đổi fit score. M5: viewer và cảnh báo suy đoán từ một ảnh giữ nguyên.
- Rủi ro: phần tay áo vẫn chưa ôm kín cánh tay ở mọi góc vì ảnh 2D không cho biết ống tay 3D và tư thế. Mặt sau quần trong ảnh kiểm tra là màu vải đồng nhất do suy đoán, nhìn như mảng xám từ góc bên; render quần riêng không có body xác nhận đó là mặt vải, không phải lỗ xuyên. Kiểm tra penetration lấy mẫu đỉnh, không chứng minh mọi tam giác không giao nhau. Váy dùng cùng sửa nhận diện mép nhưng chưa kiểm thử trực quan; composer váy giữ nhánh cũ.
- Các output chẩn đoán trong `data/outputs/` được `.gitignore` loại trừ. Bộ duyệt tự động trả `blocked by policy` khi thử xóa chúng bằng PowerShell, nên các file tạm vẫn còn cục bộ; không commit/push.

## Kiểm thử có bằng chứng

- `pytest` mục tiêu với `--import-mode=importlib`: PASS 9/9, gồm test compose, 2 test mép mở, test tự nhận diện quần và test gấu áo rỗng.
- Dựng lại áo polo và quần jeans từ ảnh thử trong `data/assets/image_tryon/`: hoàn tất, metadata hợp lệ. Thiếu SciPy gây fallback tính pháp tuyến và log cảnh báo, không làm hỏng output.
- Blender 5.2.2 trên 2 body thực tế × áo/quần: 4 lần xuất GLB thành công; mỗi báo cáo `penetration_fraction=0` và `severe_penetration_fraction=0`. Đã render áo trước/bên/sau và quần trước/bên trên body đầu tiên. Vai áo khớp hơn so với cảnh user gửi; vẫn còn sai lệch tại tay áo. Quần nhìn từ bên có phần mặt sau màu trơn, đã đối chiếu render chỉ garment.
- Chưa chạy toàn bộ API/worker/browser sau sửa. Cần khởi động lại image-tryon worker để nạp `mesh_builder.py` mới, rồi tạo job mới cho cả áo và quần; job cũ không tự cập nhật.

## Bàn giao

M3/M5 khởi động lại worker và kiểm tra job mới trong web. M2 cần template theo pose hoặc mô phỏng vải đã hiệu chuẩn cùng nhiều góc ảnh/số đo hơn nếu yêu cầu ôm chính xác ống tay, hông và ống quần. Hiện không thể bảo đảm vừa kích cỡ thực từ một ảnh và một số đo chiều dài.
