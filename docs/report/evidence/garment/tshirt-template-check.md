# Kiểm tra áo thun mẫu trên body Blender

Trạng thái: Chưa chạy test/render. Đây là kế hoạch, chưa phải evidence PASS.

## Phạm vi

Luồng body-builder, sản phẩm `demo-tshirt`, category `t_shirt`, không có
asset riêng tại `data/external/clothing/demo-tshirt.glb` hoặc `.obj`.
Asset riêng vẫn được ưu tiên. Luồng mock `/api/tryon` không đổi.

Áo mới là bề mặt mẫu tổng hợp: cổ, gấu và hai cửa tay mở; thân được lấy
khoảng hở từ đường bao lát cắt tam giác body; hướng tay được ước lượng từ đỉnh cánh tay.
Không phải mesh phục dựng từ ảnh, size chart nhà sản xuất hay mô phỏng vải.
API vẫn ghi `blender_illustrative_clothing`, source `mock` cho áo mẫu này.

Gấu áo kéo xuống từ lát cắt hông/eo kín thấp nhất trong các mức 53%, 57%,
61% chiều cao body. Không yêu cầu body có bề mặt ở khoảng trống giữa hai
chân dưới gấu. Nếu không có lát cắt tham chiếu hoặc thân trên thiếu dữ liệu,
generator vẫn báo lỗi; không tự thay bằng ellipse cố định.

Lát cắt được tách thành các thành phần liên thông, chọn thành phần trung tâm
để loại cánh tay rời. Dùng convex hull làm đường bao áo; tâm được tính từ
diện tích đường bao tại từng độ cao. Không yêu cầu tâm đoán từ bbox phải
nằm bên trong body. Đây là envelope cho áo, không phải sửa topology body.

Vai và các ring nối vai–cổ được nâng theo giao thẳng đứng với tam giác
body trong dải 74–87% chiều cao, cộng khoảng hở 6 mm tại chiều cao 1,7 m
(tỷ lệ theo chiều cao). Ring cổ cuối và gấu giữ nguyên. Đây là correction
ở đỉnh; chưa bảo đảm mọi mặt áo không xuyên sau nội suy hoặc với mọi body.

## Kiểm tra nhanh do người dùng chạy

```powershell
python -m pytest tests/unit/garment/test_tshirt_geometry.py -q
python -m pytest tests/unit/garment/test_torso_sections.py -q
```

Test TC-GAR-02 chỉ kiểm tra topology và đơn vị của bề mặt trước export,
độ tăng khoảng hở tổng hợp và lỗi lấy mẫu body. Không chứng minh độ vừa.

## Kiểm tra trực quan do người dùng thực hiện

1. Khởi động lại backend theo cách đang dùng để nạp script mới.
2. Tạo body MPFB mới ở tư thế mặc định, chọn áo thun `demo-tshirt`, size M.
3. Chọn lớp **Có trang phục**. Job/GLB cũ không tự thay đổi.
4. Xoay đủ trước, sau, hai bên và từ trên: kiểm tra cổ áo, nối vai/tay,
   gấu áo; kiểm tra thân/tay không bị xoắn hay xuyên body rõ rệt.
5. Thử S/L, đổi màu; thân áo cần thay đổi độ rộng, cổ không bị phóng to.
6. Tạo thêm body gầy và đầy đặn; ghi lại tham số nếu thấy xuyên người.
7. Thử lại một sản phẩm khác để kiểm tra luồng cũ vẫn hoạt động.

Đầu ra cần lưu: ảnh trước/sau/bên, body parameters, size, job_id,
thời gian tạo, lỗi backend nếu có. Chưa điền PASS khi chưa có kết quả.

## Giới hạn cần đánh giá

- Hỗ trợ tư thế MPFB mặc định; thiếu điểm cánh tay hoặc lấy mẫu torso
  thất bại sẽ làm job báo lỗi qua bộ xử lý hiện tại, không trả áo giả thành công.
- Vai, cổ và tay dùng tỷ lệ giải phẫu gần đúng. Chưa bảo đảm không xuyên
  trên mọi body; chưa có collision solver hay cloth simulation.
- Khoảng hở size tổng hợp, không tương ứng chu vi chart TC-GAR-04.
- Blender dùng mét/Z-up; exporter đang có chuyển GLB sang Y-up.
- Asset ngoài giữ nguyên vật liệu. Đổi swatch chưa tint texture asset ngoài;
  áo mẫu mới vẫn đổi màu như trước.
