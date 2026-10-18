# REFERENCE: EDGE CASES & TROUBLESHOOTING IN CLOTH SIMULATION (M2)

Cẩm nang chẩn đoán và khắc phục sự cố mô phỏng vật lý vải trong Blender cho Module M2.

---

## 1. Các Hiện tượng Lỗi Vật lý Phổ biến

### 1.1. Hiện tượng Nổ Mesh (Mesh Explosion / Spikes)
- **Triệu chứng:** Một vài đỉnh bị bắn văng ra vô cực, tọa độ đỉnh nhảy lên hàng nghìn mét hoặc biến thành `NaN`.
- **Nguyên nhân:** Lực va chạm quá lớn do áo khởi đầu đã nằm lẹm vào bên trong da người mẫu (Initial Intersection).
- **Cách khắc phục:**
  - Khởi tạo áo có kích thước lớn hơn cơ thể khoảng $2 - 3\text{ cm}$ trước khi kích hoạt trọng lực rơi.
  - Tăng tham số solver quality từ $5$ lên $10$ steps.

### 1.2. Áo bị tuột và rơi khỏi thân người
- **Triệu chứng:** Áo trượt qua vai và rơi tự do xuống sàn nhà.
- **Nguyên nhân:** Hệ số ma sát `collision.friction` quá nhỏ hoặc vai người mẫu dốc xuôi.
- **Cách khắc phục:**
  - Tăng `collision.friction` lên $0.8 - 1.0$.
  - Bật nhóm đỉnh ghim tạm thời (Temporary Pinning Vertex Group) ở vai trong 15 frames đầu.

### 1.3. Quá thời gian quy định (Timeout)
- **Triệu chứng:** Máy tính cấu hình yếu hoặc topology quá dày (> 30.000 đỉnh) khiến mô phỏng chạy hơn 10 phút.
- **Cách khắc phục:**
  - Sử dụng Decimate modifier trong Blender để giảm số đỉnh mesh xuống $\le 15.000 - 20.000$ vertices.
  - Script CLI bắt buộc cài đặt `signal.alarm` hoặc `threading.Timer` ngắt tiến trình sau 300 giây, trả về mã lỗi `TIMEOUT_RETRY_LOW_POLY`.
