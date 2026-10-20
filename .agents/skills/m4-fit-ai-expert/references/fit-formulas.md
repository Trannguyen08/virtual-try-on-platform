# REFERENCE: CÔNG THỨC & TIÊU CHUẨN ĐÁNH GIÁ FIT (ĐÃ ĐƯỢC PHÊ DUYỆT)

Tài liệu này ghi nhận đặc tả các công thức toán học và ngưỡng phân loại Fit đã được toàn thể dự án Virtual Try-On thống nhất phê duyệt.

---

## 1. Công thức Điểm Tổng thể Fit Score (Baseline)

Công thức tính điểm Fit tổng thể được quản lý tập trung tại hằng số cấu hình mã nguồn (`fit/score/fit_score.py`):

$$\text{Fit Score} = 0.4 \times \text{Penetration} + 0.3 \times \text{Distance} + 0.3 \times \text{Coverage}$$

Trong đó cả 3 thành phần đều được chuẩn hóa về thang điểm $[0, 100]$:
1. **Penetration Score (Điểm Xuyên thấu - Trọng số 40%):**
   - Đánh giá mức độ vải áo bị lẹm/xuyên vào bên trong cơ thể người mẫu.
   - Vải hoàn toàn ở ngoài: $\text{Penetration Ratio} = 0.0 \rightarrow \text{Score} = 100$.
   - Tỷ lệ diện tích/đỉnh xuyên thấu càng lớn thì điểm số càng giảm tuyến tính về 0.
2. **Distance Score (Điểm Khoảng cách bề mặt - Trọng số 30%):**
   - Đánh giá độ ôm của vải đối với cơ thể người dựa trên khoảng cách trung bình $d$ (đo từ vải tới bề mặt da).
   - Khoảng cách lý tưởng cho trang phục thường (Regular fit): $1.0\text{ cm} \le d \le 2.5\text{ cm} \rightarrow \text{Score} \approx 100$.
   - Quá sát ($<0.5\text{cm}$) hoặc quá rộng ($>5\text{cm}$) đều bị trừ điểm.
3. **Coverage Score (Điểm Bao phủ giải phẫu - Trọng số 30%):**
   - Đánh giá khả năng che phủ đúng và đủ vùng cơ thể mục tiêu (ví dụ: áo T-shirt phải che kín ngực, eo và vai).
   - Nếu áo bị kéo lệch, hở vai hoặc co cụm thì điểm Coverage sẽ giảm theo tỷ lệ phần trăm vùng bị thiếu.

---

## 2. Tiêu chuẩn Phân loại Vùng (Region Fit Categorization)

Cơ thể được phân đoạn (vertex segmentation) thành 4 vùng cơ bản: **Chest (Ngực)**, **Waist (Eo)**, **Shoulder (Vai)**, **Hip (Hông)**.

Mỗi vùng được phân loại thành 3 trạng thái dựa trên khoảng cách trung bình $d$ từ vải tới da của vùng đó:

| Nhãn Phân loại | Ý nghĩa | Ngưỡng Khoảng cách (Đề xuất đã duyệt) |
| :--- | :--- | :--- |
| **`TIGHT`** | Quần áo bị chật, bó sát hoặc bị căng kéo quá mức | $d < 0.5\text{ cm}$ (hoặc có tỷ lệ xuyên thấu cao) |
| **`GOOD`** | Quần áo vừa vặn, ôm thoải mái theo cơ thể | $0.5\text{ cm} \le d \le 3.0\text{ cm}$ |
| **`LOOSE`** | Quần áo bị rộng, thụng hoặc bay xa khỏi người mẫu | $d > 3.0\text{ cm}$ |

---

## 3. Quy ước Nguồn Chân lý Duy nhất (Single Source of Truth)
- Toàn bộ các trọng số ($0.4 / 0.3 / 0.3$) và ngưỡng phân loại trên **phải được khai báo thành các hằng số (constants) tại một file duy nhất trong code** (`fit/score/fit_score.py`).
- Mọi module khác, file test và tài liệu đều chỉ tham chiếu tới hằng số này, tuyệt đối không hard-code các con số rải rác trong mã nguồn.
