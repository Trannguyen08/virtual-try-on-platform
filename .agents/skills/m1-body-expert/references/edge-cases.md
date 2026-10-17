# REFERENCE: EDGE CASES & ERROR RECOVERY (M1)

Cẩm nang xử lý các trường hợp ngoại lệ cho Module M1 trong môi trường thực tế.

---

## 1. Các Tình huống Dị thường Phổ biến

### 1.1. Ảnh không toàn thân (Crop chân hoặc crop đầu)
- **Hiện tượng:** MediaPipe không phát hiện được mắt cá chân hoặc mũi ($confidence < 0.5$).
- **Xử lý:**
  - Báo lỗi có kiểm soát: Trả về exception `InvalidImageError` kèm mã lỗi `INVALID_IMAGE_CROPPED`.
  - Gợi ý người dùng chụp ảnh đứng lùi xa khoảng 2 - 3 mét để lấy đủ đỉnh đầu đến gót chân.

### 1.2. Ảnh không có người (Ảnh phong cảnh, xe cộ, thú cưng)
- **Hiện tượng:** MediaPipe Pose trả về `results.pose_landmarks is None`.
- **Xử lý:**
  - Bắt lỗi ngay tại tầng preprocessing: Trả về `NO_PERSON_FOUND`. Tuyệt đối không cho chạy vào thuật toán tối ưu mesh.

### 1.3. Trang phục thùng thình (Áo khoác gió to, váy xòe)
- **Hiện tượng:** Cắt lớp mesh bị phình to bất thường ở vòng ngực và hông do ảnh chụp trang phục quá rộng.
- **Xử lý:**
  - Áp dụng kỹ thuật Regularization prior: Ràng buộc tham số shape $\|\beta\|_2^2 \le \gamma$ để không làm biến dạng dị dạng mô hình SMPL-X.
  - Cho phép người dùng nhập trực tiếp chiều cao và số đo thước dây thật để hiệu chỉnh lại lát cắt.
