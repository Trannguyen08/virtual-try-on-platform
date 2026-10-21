# CHANGE IMPACT LOG 1/2: GUIDED CIELAB SEGMENTATION, PROP PRUNING & AUTO GARMENT TYPE DETECTION

- **Mã đợt thay đổi:** `20261019_160000_M2_guided_segmentation_prop_pruning_and_auto_garment_type`
- **Module:** M2 (Garment Reconstruction & Saliency Extraction) & M5 (Garment3DPage UI)
- **Thời điểm:** 2026-10-19 16:00:00 (Asia/Saigon)
- **Tác giả:** Agent Role M2 Garment Expert
- **Phạm vi gộp:** Hợp nhất toàn bộ các cải tiến tách nền, bảo tồn tay áo và tự động nhận diện loại đồ (từ 14:56 đến 16:00).

---

## 1. Vấn đề giải quyết & Nguyên nhân Gốc rễ (Root Cause Analysis)

### 1.1. Lỗi cụt/mất 2 tay áo trên áo thun và áo bóng đá (Severed Sleeves):
- **Nguyên nhân:** Thuật toán cũ áp dụng `cv2.distanceTransform(binary)` với ngưỡng đỉnh `0.35 * max_dist`. Đối với áo dang tay, nách áo hẹp hơn độ dày tay áo khiến watershed phân tách áo thành 3 đỉnh độc lập (thân, tay trái, tay phải) và chém đứt 2 tay áo ở nách, sau đó chỉ giữ lại thân áo.
- **Giải pháp triệt để:** Bỏ hoàn toàn cơ chế cắt watershed dựa trên khoảng cách hình học. Tay áo và thân áo là cùng một vật thể liền khối, cùng chất liệu vải nên luôn được bảo tồn nguyên vẹn 100%.

### 1.2. Lỗi nhận diện nhầm áo bóng đá thành quần (Soccer Kit Jersey Misidentification):
- **Nguyên nhân:** Trong ảnh chụp bộ kit bóng đá (áo trắng + quần đùi đen gấp ở góc dưới), nền có độ tương phản phức tạp khiến thuật toán cũ giữ lại chiếc quần đen và bỏ chiếc áo trắng.
- **Giải pháp:** Tích hợp bộ đánh giá độ nổi bật đa tiêu chí (Saliency Scoring Engine):
  - Ưu tiên đối tượng có tâm nằm gần tâm ảnh hơn.
  - Ưu tiên đối tượng có diện tích lớn hơn và độ rọi sáng phù hợp với trang phục chính.
  - Phân tích màu sắc CIELAB 16 phân đoạn biên để ước lượng nền thảm/sàn chính xác, cô lập đúng chiếc áo và loại bỏ chiếc quần đùi phụ.

### 1.3. Lỗi dính đạo cụ góc chụp (Peripheral Prop Pruning):
- **Giải pháp:** Phân tích màu sắc viền ảnh với đồng thuận đa phân đoạn, đánh dấu các góc có logo banner (Kiwi Sport), bảng clapperboard, chân máy hoặc giày thành vùng nền (`GC_BGD`) và khởi tạo `cv2.grabCut` 4 trạng thái (`GC_INIT_WITH_MASK`). Bất kỳ chi tiết thừa nào ở góc có sai lệch màu nghiêm trọng (ΔE > 55) đều được bóc tách sạch sẽ.

### 1.4. Tự động nhận diện loại trang phục (Auto Garment Type Detection):
- Loại bỏ hoàn toàn form thủ công "Bước 2: Chọn loại đồ & kích thước thật (cm)" trên giao diện người dùng.
- Hàm `auto_detect_garment_type` tự động phân tích hình học contour:
  - Tách 2 ống chân ở thân dưới → `pants` (quần).
  - Có cánh tay áo mở rộng hai bên (W_chest > W_waist) → `tshirt` / `shirt` (áo).
  - Thân dài liền khối → `dress` (đầm); xòe dần xuống đáy → `skirt` (chân váy).

---

## 2. Danh mục File Thay đổi

| STT | File | Thay đổi chính |
| :---: | :--- | :--- |
| 1 | `garment/reconstruction/segmentation.py` | Tách nền CIELAB 16 phân đoạn, GrabCut định hướng lõi thân áo, bảo tồn tay áo, lọc đạo cụ góc và cô lập trang phục nổi bật. |
| 2 | `garment/reconstruction/classifier.py` | Thuật toán `auto_detect_garment_type` phân loại tự động 4 nhóm trang phục. |
| 3 | `garment/reconstruction/contracts.py` | Bổ sung `"auto"` vào `SUPPORTED_GARMENT_TYPES`. |
| 4 | `backend/garment3d/router.py` | Cho phép tham số `garment_type: str = "auto"`. |
| 5 | `frontend/src/api/garment3d.ts` | Bổ sung `'auto'` vào kiểu `GarmentType` và payload submit. |
| 6 | `frontend/src/pages/Garment3DPage.tsx` | Xóa bỏ khối Bước 2, chuyển sang cơ chế 1-click tự động nhận diện và hiển thị huy hiệu loại đồ. |
| 7 | `frontend/src/components/GarmentImageInputs.tsx` | Đổi nhãn `Bước 1` thành `Tải ảnh trang phục`. |
| 8 | `tests/unit/garment/reconstruction/test_local_pipeline.py` | Bổ sung `TC-GARMENT-08` (auto-detect tshirt và bảo tồn 2 tay áo) và `TC-GARMENT-09` (auto-detect pants). |

---

## 3. Kiểm thử & Đánh giá

- `TC-GARMENT-08`: Vượt qua (Pass), áo thun và áo bóng đá giữ nguyên vẹn 2 tay áo, tự nhận diện đúng `tshirt`.
- `TC-GARMENT-09`: Vượt qua (Pass), quần dài tự nhận diện đúng `pants`.
