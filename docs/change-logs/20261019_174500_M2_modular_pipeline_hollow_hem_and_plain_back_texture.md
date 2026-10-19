# CHANGE IMPACT LOG 2/2: MODULAR ARCHITECTURE, HOLLOW HEM & PLAIN DOMINANT-COLOR BACK SURFACE

- **Mã đợt thay đổi:** `20261019_174500_M2_modular_pipeline_hollow_hem_and_plain_back_texture`
- **Module:** M2 (Garment Reconstruction & Parametric 3D Generation)
- **Thời điểm:** 2026-10-19 17:45:00 (Asia/Saigon)
- **Tác giả:** Agent Role M2 Garment Expert
- **Phạm vi gộp:** Hợp nhất toàn bộ các cải tiến tái cấu trúc kiến trúc, mở rỗng đáy áo và tạo mặt sau trơn màu chủ đạo (từ 16:30 đến 17:47).

---

## 1. Vấn đề giải quyết & Các Cải tiến Chính

### 1.1. Tái cấu trúc Module hóa Pipeline (`local_pipeline.py`):
- **Bối cảnh:** File `local_pipeline.py` trước đây là một file monolith dài gần 1.500 dòng chứa lẫn lộn từ xử lý ảnh, phân loại, đo đạc nhân trắc đến dựng mesh 3D, rất khó bảo trì và dễ xung đột.
- **Giải pháp:** Tách thành 5 module chuyên trách theo kiến trúc Single Responsibility:
  - `garment/reconstruction/classifier.py`: Tự động phân loại 4 nhóm trang phục.
  - `garment/reconstruction/segmentation.py`: Pipeline tách nền, bảo tồn tay áo và chi tiết gốc.
  - `garment/reconstruction/landmarks.py`: Trích xuất điểm mốc giải phẫu & số đo pixel.
  - `garment/reconstruction/scaling.py`: Hiệu chuẩn tỷ lệ pixel sang mét/cm.
  - `garment/reconstruction/mesh_builder.py`: Dựng mesh 3D parametric, xử lý rỗng cửa hở và vật liệu PBR.
  - `garment/reconstruction/local_pipeline.py`: Giữ lại bộ điều phối `LocalGarmentReconstructor` gọn nhẹ (< 200 dòng), 100% tương thích ngược các API và test suite.

### 1.2. Đáy áo nhìn xuyên thấu, loại bỏ chi tiết thừa (Hollow See-Through Bottom Hem):
- **Nguyên nhân:** Thuật toán cũ tạo các tam giác vách nối (seam wall) bắc cầu qua toàn bộ chu vi đường biên, khiến gấu áo bị bịt kín bởi các mặt phẳng chéo hoặc sinh ra các vấu nhọn thừa thãi.
- **Giải pháp:** Nhận diện chính xác các cửa hở giải phẫu (`hem`, `neck`, `left_cuff`, `right_cuff`) và **bỏ qua hoàn toàn** việc tạo tam giác nối tại các vùng này:
  - Đáy gấu áo mở rỗng 100% thành hình vành khuyên elip mềm mại.
  - Người dùng xoay áo và nhìn từ dưới lên có thể nhìn xuyên thấu qua thân áo lên tới cổ áo như một chiếc áo thật.

### 1.3. Mặt sau là mặt trơn mang màu chủ đạo của mặt trước (Plain Dominant Color Back Surface):
- **Nguyên nhân:** Khi người dùng chỉ tải ảnh mặt trước (`back_rgb is None`), hệ thống cũ tái sử dụng nguyên văn texture mặt trước làm texture mặt sau, khiến logo, huy hiệu câu lạc bộ, tem nhãn cổ và hoa văn mặt trước bị in sao chép ra sau lưng.
- **Giải pháp:** 
  - Tự động trích xuất màu sắc chủ đạo của trang phục mặt trước: `fabric_color = np.median(front_rgb[mask])`.
  - Khởi tạo texture mặt sau `GarmentBack` thành một **bề mặt vải trơn sạch sẽ (plain blank surface)** mang đúng màu chủ đạo này.
  - **Kết quả:** Mặt trước giữ nguyên đầy đủ huy hiệu và logo thực tế; mặt sau là lưng áo trơn màu chủ đạo sạch sẽ, tự nhiên. Hệ thống đổ bóng PBR trong Three.js vẫn tạo hiệu ứng ánh sáng 3D chân thực theo đường cong lưng áo.
  - Nếu người dùng tải ảnh mặt sau riêng, hệ thống vẫn ưu tiên áp dụng đúng ảnh mặt sau đó.

### 1.4. Bảo tồn nguyên trạng chi tiết thật, loại bỏ suy đoán chắp vá:
- Giữ nguyên vẹn 100% kết quả tách nền thực tế từ ảnh chụp, không can thiệp vẽ thêm hoặc kéo giãn hình học nhân tạo, giúp hệ thống vận hành ổn định, nhẹ nhàng và chính xác.

---

## 2. Danh mục File Thay đổi

| STT | File | Vai trò |
| :---: | :--- | :--- |
| 1 | `garment/reconstruction/local_pipeline.py` | Lớp điều phối tổng thể gọn nhẹ, chuẩn hóa quy trình reconstruct. |
| 2 | `garment/reconstruction/mesh_builder.py` | Tạo mesh 3D parametric, gấu áo rỗng xuyên thấu và mặt sau trơn màu chủ đạo. |
| 3 | `garment/reconstruction/segmentation.py` | Quản lý quy trình tách nền sắc nét, giữ trọn vẹn chi tiết gốc của trang phục. |
| 4 | `garment/reconstruction/classifier.py` | Phân loại loại đồ tự động. |
| 5 | `garment/reconstruction/landmarks.py` | Trích xuất điểm mốc và đo đạc kích thước. |
| 6 | `garment/reconstruction/scaling.py` | Hiệu chuẩn kích thước thực tế. |
| 7 | `tests/unit/garment/reconstruction/test_local_pipeline.py` | Bổ sung và cập nhật `TC-GARMENT-10`, `TC-GARMENT-11`, `TC-GARMENT-12`, `TC-GARMENT-13`. |

---

## 3. Kiểm thử & Đánh giá

- `TC-GARMENT-10`: Vượt qua (Pass), gấu áo là cửa hở rỗng không có tam giác bịt đáy.
- `TC-GARMENT-11`: Vượt qua (Pass), áo có vết khuyết dựng mesh 3D hợp lệ không lỗi.
- `TC-GARMENT-12`: Vượt qua (Pass), áo chụp nghiêng dựng mesh 3D hợp lệ ở tư thế tự nhiên.
- `TC-GARMENT-13`: Vượt qua (Pass), mặt sau trang phục sử dụng texture trơn màu đồng nhất mang màu chủ đạo của mặt trước.
