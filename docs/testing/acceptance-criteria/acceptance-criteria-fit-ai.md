# TIÊU CHUẨN NGHIỆM THU (ACCEPTANCE CRITERIA FRAMEWORK)
**Dự án:** Virtual Try-On Platform  
**Phiên bản:** 1.0  
**Tài liệu quy định chất lượng nghiệm thu:** Dùng chung cho toàn bộ thành viên và các mốc bàn giao.

---

## 1. QUY ƯỚC CHUNG VỀ ĐIỀU KIỆN NGHIỆM THU

### 1.1. Định nghĩa Hoàn thành (Definition of Done - DoD) cho một Task
Một task chỉ được coi là hoàn thành (Done / Ready for Review) khi đáp ứng đủ 4 điều kiện:
1. **Code & Cleanliness:** Mã nguồn tuân thủ coding conventions, không còn debug print thừa, có đầy đủ Type hints và Docstrings.
2. **Unit / Module Test:** Đã viết test case tương ứng trong `tests/` và test đạt trạng thái **PASS 100%**.
3. **CI Status:** Pull Request được mở vào nhánh `develop`, toàn bộ pipeline CI trên GitHub Actions báo **Xanh (PASS)**.
4. **Evidence Log:** Kết quả kiểm thử (chỉ số, bảng số liệu, ảnh chụp 3D) đã được cập nhật vào [test-cases.md](file:///d:/Năm%204%20-%20Kỳ%201/Project/virtual-tryon/virtual-try-on-platform/docs/testing/test-cases.md) và lưu file minh chứng trong `docs/report/evidence/<module>/`.

---

## 2. TIÊU CHUẨN NGHIỆM THU CHI TIẾT THEO TỪNG MODULE

### 📐 2.1. Module M4 — Fit Engine & AI Models (Owner: M4)

| Thành phần | Tiêu chí kỹ thuật (Acceptance Criteria) | Phương pháp kiểm thử | Điều kiện PASS / FAIL |
| :--- | :--- | :--- | :--- |
| **Penetration Metric (FIT-01)** | - Tính toán tỉ lệ xuyên thấu giữa vải và cơ thể.<br>- Áo hoàn toàn bên ngoài $\rightarrow \text{Ratio} = 0$. | `pytest tests/unit/fit/` với mesh giải tích (khối cầu lồng nhau). | **PASS:** Garment ngoài $\rightarrow 0$; Garment xuyên $\rightarrow$ sai số $\le 2\%$ so với giải tích toán học. |
| **Distance Metric (FIT-02)** | - Tính khoảng cách bề mặt trung bình và khoảng cách per-vertex.<br>- Độ dài mảng distance bằng chính xác số đỉnh mesh áo. | `pytest` trên mesh vỏ cầu cách đều 2.0 cm. | **PASS:** Khoảng cách tính ra đạt $2.0 \pm 0.1\text{ cm}$; Không có giá trị âm hoặc NaN. |
| **Coverage Metric (FIT-03)** | - Đo tỉ lệ vùng giải phẫu cơ thể được trang phục che phủ hợp lệ. | `pytest` với mesh áo nguyên vẹn và mesh áo bị cắt bỏ 50%. | **PASS:** Áo chuẩn $\approx 1.0$; Áo cắt nửa $\approx 0.5$ (sai số $\le 5\%$). |
| **Region Fit (FIT-04)** | - Phân loại 4 vùng chính (*Chest, Waist, Shoulder, Hip*).<br>- Nhãn phân loại $\in \{\text{TIGHT, GOOD, LOOSE}\}$. | `pytest` với các khoảng cách giả lập biên: chật ($<0.5\text{cm}$), vừa ($0.5-3.0\text{cm}$), rộng ($>3.0\text{cm}$). | **PASS:** 100% các vùng được gán nhãn chính xác theo ngưỡng quy định. |
| **Fit Score Formula (FIT-05)** | - Điểm tổng hợp: $\text{Fit} = 0.4\text{Pen} + 0.3\text{Dist} + 0.3\text{Cov}$.<br>- Giá trị điểm nằm nghiêm ngặt trong đoạn $[0, 100]$. | `pytest` với các bộ giá trị biên và trường hợp điển hình. | **PASS:** Điểm tính đúng công thức (sai số $\le 0.05$ điểm); Nhãn tổng thể khớp với điểm số. |
| **Heatmap JSON (FIT-06)** | - Xuất file `heatmap.json` theo đúng định dạng Data Contract. | `pytest` + `jsonschema.validate`. | **PASS:** Validate $100\%$ theo JSON Schema; Số giá trị khớp số đỉnh mesh. |
| **Size Dataset v1 (AI-01)** | - Sinh bộ dữ liệu số đo người giả lập (Synthetic Dataset).<br>- Dữ liệu chia thành 3 tập: Train ($70\%$), Val ($15\%$), Test ($15\%$). | Script kiểm tra thống kê phân phối. | **PASS:** Không chứa giá trị NaN; Số đo nằm trong khoảng sinh lý người; Mỗi size ($S, M, L, XL$) chiếm $\ge 10\%$ tổng mẫu. |
| **Size Recommender (AI-02)** | - Huấn luyện model (Random Forest / XGBoost / MLP).<br>- Dự đoán Size kèm độ tin cậy Confidence $[0, 1]$. | Đánh giá trên tập kiểm thử độc lập (Test set). | **PASS:** Độ chính xác Accuracy $\ge 85\%$ trên test set synthetic; Tỉ lệ đoán sai lệch quá 1 size $\le 2\%$. |
| **Fit Dataset v1 (AI-03)** | - Sinh dataset đặc trưng hình học & chênh lệch số đo. | Thống kê nhãn trên file CSV sinh ra. | **PASS:** Đủ 3 nhãn `Too Tight / Good / Too Loose`; Mỗi nhãn chiếm $\ge 15\%$ tổng tập. |
| **Fit Predictor & Classifier (AI-04)** | - Dự đoán Fit Score (Hồi quy) và Phân loại Fit Class. | Đánh giá sai số hồi quy và phân loại đa lớp. | **PASS:** MAE $\le 5.0$ điểm Fit; Macro-F1 Score $\ge 0.75$. |
| **Inference & Fallback (AI-07)** | - Đóng gói package `FitPredictor` tích hợp vào hệ thống.<br>- Có cơ chế tự động chuyển về Geometry khi AI lỗi. | Test mô phỏng khi thiếu feature hoặc tắt cờ AI. | **PASS:** Thời gian inference $\le 1.0\text{ s}$; Fallback hoạt động $100\%$ không gây sập hệ thống (zero crash). |



## 3. TIÊU CHUẨN NGHIỆM THU THEO CÁC MỐC MILESTONE

- **Mốc MS-0 (Foundation):** Toàn bộ tài liệu Architecture, Git workflow, API contract, Testing framework và CI skeleton được 100% thành viên xác nhận.
- **Mốc MS-1 (Mock E2E - Release v0.1):** Luồng upload ảnh $\rightarrow$ gọi API Mock $\rightarrow$ hiển thị giao diện 3D chạy thông suốt trên CI.
- **Mốc MS-3 (Baseline Real E2E - Release v0.5):** Pipeline thật chạy thành công từ Ảnh $\rightarrow$ 3D Body $\rightarrow$ Draping $\rightarrow$ Đo đạc Geometry trên $\ge 90\%$ (ít nhất 9/10) ảnh test.
- **Mốc MS-4 (AI Integration):** Tích hợp hoàn tất mô hình AI Size Recommendation và Fit Prediction vào hệ thống; Có cơ chế fallback; Báo cáo đánh giá đối chiếu AI vs Geometry đầy đủ.
