# REFERENCE: LANDMARKS & MESH SLICING SPECIFICATIONS (M1)

Tài liệu tham khảo đặc tả chi tiết 33 MediaPipe pose keypoints và phương pháp cắt lớp mesh 3D để trích xuất 5 số đo nhân trắc học cho Module M1.

---

## 1. Bản đồ 33 MediaPipe Pose Keypoints

| Index | Keypoint Name | Vị trí giải phẫu | Sử dụng trong M1 |
| :---: | :--- | :--- | :--- |
| `0` | `NOSE` | Mũi | Căn chỉnh tâm mặt, xác định đỉnh đầu |
| `11, 12` | `LEFT_SHOULDER, RIGHT_SHOULDER` | 2 đầu mỏm cùng vai | Xác định chiều rộng vai (Shoulder width) |
| `23, 24` | `LEFT_HIP, RIGHT_HIP` | 2 khớp háng / xương chậu | Xác định vị trí mặt phẳng cắt Hông (Hip) |
| `27, 28` | `LEFT_ANKLE, RIGHT_ANKLE` | 2 mắt cá chân | Xác định đáy chân để đo Chiều cao |
| `31, 32` | `LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX` | 2 ngón chân cái | Xác định mặt phẳng tiếp đất |

---

## 2. Phương pháp Cắt lớp Mesh (Mesh Slicing Planes)

Tọa độ hệ trục chuẩn: **Y-up** (Trục Y là chiều cao đứng, mặt phẳng XZ là mặt phẳng ngang cắt ngang cơ thể).

Giả sử chiều cao cơ thể người từ đỉnh đầu ($y_{max}$) đến gót chân ($y_{min}$) là $H = y_{max} - y_{min}$:

| Số đo | Tọa độ lát cắt $Y$ đề xuất | Khoảng nhân trắc học hợp lệ | Phương pháp tính chu vi |
| :--- | :--- | :---: | :--- |
| **Chiều cao (Height)** | $H = y_{max} - y_{min}$ | $140 - 210\text{ cm}$ | Khoảng cách đỉnh đầu tới mặt sàn |
| **Rộng vai (Shoulder)** | Khoảng cách Euclid giữa 2 điểm vai $P_{11}$ và $P_{12}$ | $30 - 60\text{ cm}$ | $\|P_{11} - P_{12}\|_2$ (chiếu ngang) |
| **Vòng ngực (Chest/Bust)** | $y_{chest} \approx y_{min} + 0.72 \times H$ | $60 - 140\text{ cm}$ | Giao tuyến tam giác mesh với mặt phẳng $Y = y_{chest}$ |
| **Vòng eo (Waist)** | $y_{waist} \approx y_{min} + 0.58 \times H$ | $50 - 130\text{ cm}$ | Tìm lát cắt có chu vi nhỏ nhất vùng thân giữa |
| **Vòng hông (Hip)** | $y_{hip} \approx y_{min} + 0.50 \times H$ | $70 - 150\text{ cm}$ | Tìm lát cắt có chu vi lớn nhất vùng xương chậu |

---

## 3. Thuật toán Tính Chu vi Lát cắt Kín
1. Xác định tập hợp tất cả các cạnh tam giác cắt ngang mặt phẳng $Y = y_0$.
2. Mỗi tam giác bị cắt sẽ tạo ra 1 đoạn thẳng gồm 2 điểm giao.
3. Sắp xếp các đoạn thẳng thành một đa giác khép kín tuần tự.
4. Tổng độ dài chu vi:
   $$\text{Circumference} = \sum_{i=1}^{N} \|\mathbf{p}_{i+1} - \mathbf{p}_i\|_2$$
5. Đổi đơn vị từ mét sang centimet ($1\text{ m} = 100\text{ cm}$) và làm tròn về 1 chữ số thập phân (`round(1)` = 1 mm).
