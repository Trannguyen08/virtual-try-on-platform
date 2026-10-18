# REFERENCE: BLENDER CLOTH SIMULATION CONFIGURATION (M2)

Đặc tả các thông số vật lý vải và câu lệnh thực thi mô phỏng Blender headless CLI cho Module M2.

---

## 1. Cấu trúc Lệnh CLI Blender Headless
Lệnh thực thi không có giao diện đồ họa (Headless):
```bash
blender --background --factory-startup --python garment/simulation/drape.py -- \
  --body data/test_assets/body.obj \
  --garment garment/mesh/tshirt_template.obj \
  --size M \
  --output data/outputs/draped.glb \
  --timeout 300
```

---

## 2. Bảng Tham số Vật lý Vải Tiêu chuẩn (Cotton T-Shirt)

| Nhóm thuộc tính | Tham số Blender bpy | Giá trị khuyến nghị | Ý nghĩa thực tế |
| :--- | :--- | :---: | :--- |
| **Khối lượng (Mass)** | `cloth.settings.mass` | $0.20\text{ kg/m}^2$ | Độ nặng tiêu chuẩn của vải cotton 100% |
| **Độ cứng căng (Tension)** | `cloth.settings.tension_stiffness` | $18.0$ | Chống dãn dài quá mức theo chiều dọc sợi |
| **Độ cứng nén (Compression)** | `cloth.settings.compression_stiffness` | $18.0$ | Giữ phom vải khi bị co ép |
| **Độ cứng uốn (Bending)** | `cloth.settings.bending_stiffness` | $0.75$ | Tạo nếp gấp mềm mại tự nhiên quanh ngực/eo |
| **Giảm chấn (Damping)** | `cloth.settings.damping.tension` | $5.0$ | Triệt tiêu dao động rung lắc nhanh chóng |
| **Ma sát vải (Friction)** | `cloth.collision_settings.friction` | $5.0$ | Ma sát giữa các lớp vải khi xếp nếp |
| **Khoảng cách va chạm** | `cloth.collision_settings.distance_min` | $0.005\text{ m}$ (5 mm) | Giữ lớp vải không bị lẹm vào da người mẫu |

---

## 3. Quy chuẩn Khung hình Mô phỏng (Simulation Timeline)
- **Start frame:** $1$
- **End frame:** $40 - 50$ (Đủ để vải rơi tự do từ vị trí chuẩn bị và ôm khít cơ thể ở trạng thái tĩnh).
- **Sub-frame steps:** $5 - 8$ (Tăng độ chính xác chống xuyên thấu).
- **Trạng thái ổn định:** Lấy mesh ở frame cuối cùng (settled frame) để xuất ra file `draped.glb`.
