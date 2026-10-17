# REFERENCE: SMPL-X 3D MODEL SPECIFICATIONS (M1)

Tài liệu tham khảo về cấu trúc mô hình tham số SMPL-X và các ràng buộc kỹ thuật.

---

## 1. Thông số Kỹ thuật Chuẩn SMPL-X
- **Số đỉnh (Vertices):** Chính xác **$10.475$ vertices**.
- **Số mặt (Faces):** $20.908$ tam giác.
- **Tham số Hình dạng (Shape $\beta$):** Vector $\beta \in \mathbb{R}^{10}$ (hoặc $\mathbb{R}^{16}$) biểu diễn các đặc điểm hình thể (gầy/béo, cơ bắp, tỷ lệ chi) theo phân tích thành phần chính (PCA).
- **Tham số Tư thế (Pose $\theta$):** Bao gồm body pose ($21$ khớp $\times 3 = 63$), jaw pose ($3$), eye pose ($6$), hand pose ($2 \times 12 = 24$).
- **Gốc tọa độ (Origin):** Khớp xương cùng (Pelvis) nằm tại $(0, 0, 0)$.
- **Hệ trục tọa độ chuẩn:** **Y-up, +Z forward, Right-handed**.
- **Đơn vị hình học:** **Mét (m)**. Chiều cao người Việt Nam trung bình khoảng $1.55 - 1.80\text{ m}$.

---

## 2. Tiêu chuẩn File Xuất (Export Requirements)
1. **Định dạng:** `.glb` (cho Web và Three.js) và `.obj` (cho Blender CLI mô phỏng).
2. **Kiểm tra tính toàn vẹn (Integrity Check):**
   - Đảm bảo $100\%$ không chứa tọa độ `NaN` hoặc `Inf`.
   - Không có mặt tam giác bị suy biến (diện tích bằng 0).
   - Pháp tuyến bề mặt (Face Normals) hướng ra ngoài.
