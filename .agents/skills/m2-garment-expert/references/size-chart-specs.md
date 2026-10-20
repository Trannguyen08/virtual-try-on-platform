# REFERENCE: GARMENT SIZE CHART & SCALING SPECIFICATIONS (M2)

Bảng thông số kích thước tiêu chuẩn và nguyên tắc co dãn (Scaling/Morphing) mesh quần áo cho Module M2.

---

## 1. Bảng Size Chart Tiêu chuẩn (T-Shirt Regular Fit)

Các thông số kích thước được đo theo chu vi và chiều dài trên bề mặt phẳng (Đơn vị: Centimet):

| Thông số | Size S | Size M | Size L | Size XL | Bước nhảy (Grade) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Vòng ngực áo (Garment Chest)** | $94.0\text{ cm}$ | $100.0\text{ cm}$ | $106.0\text{ cm}$ | $112.0\text{ cm}$ | $+6.0\text{ cm}$ / size |
| **Dài áo (Garment Length)** | $66.0\text{ cm}$ | $68.0\text{ cm}$ | $70.0\text{ cm}$ | $72.0\text{ cm}$ | $+2.0\text{ cm}$ / size |
| **Rộng vai áo (Garment Shoulder)** | $42.0\text{ cm}$ | $44.0\text{ cm}$ | $46.0\text{ cm}$ | $48.0\text{ cm}$ | $+2.0\text{ cm}$ / size |
| **Dài tay (Sleeve Length)** | $20.0\text{ cm}$ | $21.0\text{ cm}$ | $22.0\text{ cm}$ | $23.0\text{ cm}$ | $+1.0\text{ cm}$ / size |

*Tính đơn điệu bắt buộc:* $S < M < L < XL$ đối với mọi số đo.

---

## 2. Nguyên tắc Biến dạng Mesh (Mesh Morphing & Scaling)
- Giả sử mesh gốc là Size M (chu vi $C_M = 100.0\text{ cm}$).
- Để sinh mesh Size $X$ ($X \in \{S, L, XL\}$):
  - Hệ số co dãn chiều ngang (Radial scale): $s_{xz} = \frac{C_X}{C_M}$
  - Hệ số co dãn chiều dài (Vertical scale): $s_y = \frac{L_X}{L_M}$
- Sau khi scale, áp dụng thuật toán đo chu vi ngực trên mesh cắt lớp:
  $$\|C_{\text{mesh\_measured}} - C_{\text{size\_chart}}\| \le 1.0\text{ cm}$$
