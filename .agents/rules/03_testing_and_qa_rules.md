# RULE 03: TESTING, QA & EVIDENCE LOGGING

## 1. Tham chiếu Bắt buộc (Mandatory Reference)
Trước khi viết bất kỳ bài test nào cho M4, Agent **BẮT BUỘC** phải đọc và đối chiếu 2 tài liệu:
1. `docs/testing/test-strategy.md` (Chiến lược kiểm thử và phân tầng 7 cấp).
2. `docs/testing/test-cases/test-cases-fit-ai.md` (Danh mục ID test case đã chốt).

---

## 2. Quy chuẩn Viết Code Kiểm thử (Test Implementation Standards)

### 2.1. Đặt tên hàm và Định dạng ID Truy vết (Traceability)
Mỗi hàm kiểm thử phải gắn liền với mã Test Case đã định nghĩa:
- Tên hàm chuẩn: `test_<ten_chuc_nang>_tc_<id>()` (viết chữ thường).
- Bắt buộc ghi rõ Docstring chuẩn ở đầu hàm test:
```python
def test_penetration_ratio_tc_fit_01():
    """
    Test Case ID: TC-FIT-01
    Target: Kiểm tra tỷ lệ xuyên thấu (Penetration) với mesh giải tích khối cầu.
    Expected: Garment ngoài body -> Ratio = 0.0; Garment lồng trong body -> khớp giải tích.
    """
    # Code test ở đây...
```

### 2.2. So sánh Số thực (Float Approximation)
- Đối với mọi phép so sánh khoảng cách hình học, diện tích, tỷ lệ, **BẮT BUỘC dùng `pytest.approx`**:
```python
assert penetration_ratio == pytest.approx(0.0, abs=1e-4)
assert avg_distance == pytest.approx(0.02, abs=1e-3)  # Đơn vị mét
```

### 2.3. Tái lập Kết quả AI (Seed Fixing)
- Mọi bài test liên quan đến Dataset generation, chia tách dữ liệu (split), và mô hình AI **bắt buộc phải cố định Random Seed**:
```python
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)
```

### 2.4. Kiểm thử Bắt buộc cho Cơ chế Dự phòng (Fallback Mechanism)
- Module AI bắt buộc phải có Unit test kiểm tra kịch bản sự cố: Khi model AI bị lỗi, file weights bị thiếu, hoặc input bị thiếu feature, hệ thống phải **tự động fallback về tính toán Geometry an toàn, tuyệt đối không được sập chương trình (zero crash)**.

---

## 3. Ngưỡng Tiêu chuẩn Nghiệm thu Tối thiểu cho Model AI

Mọi mô hình do M4 huấn luyện phải đạt các ngưỡng số thực nghiệm tối thiểu sau trước khi được phép tích hợp:
- **Size Recommender v1 (AI-02):** `Accuracy >= 85%` trên tập test synthetic; tỷ lệ dự đoán lệch quá 1 size `<= 2%`.
- **Fit Predictor Regression (AI-04):** `MAE <= 5.0 điểm` Fit Score (trên thang 100).
- **Fit Classifier (AI-04):** `Macro-F1 >= 0.75` cho 3 lớp (`Too Tight / Good Fit / Too Loose`).
- **Thời gian suy luận (Inference Latency):** `<= 1.0 giây` cho mỗi lượt dự đoán trên CPU.

---

## 4. Quy định về Tốc độ Test & Pytest Markers
- **Tiêu chí "Dưới 2 giây":** Áp dụng cho **TỪNG test case đơn lẻ** trong bộ Fast Unit Test, không áp dụng cho tổng thời gian của toàn bộ suite.
- **Marker bắt buộc:**
  - `@pytest.mark.fast` (hoặc mặc định): Test toán học nhẹ, chạy được ngay trên GitHub Actions CI.
  - `@pytest.mark.slow`: Test chạy batch, đọc file lớn, kiểm tra huấn luyện.
  - `@pytest.mark.gpu`: Test yêu cầu card đồ họa CUDA.

---

## 5. Quy trình Lưu trữ Bằng chứng (Evidence Logging)
Sau khi User chạy test có kết quả:
1. Agent cập nhật trạng thái `PASS/FAIL` và kết quả thực tế vào bảng `docs/testing/test-cases/test-cases-fit-ai.md`.
2. Hướng dẫn User lưu file minh chứng (ảnh đồ thị confusion matrix, log terminal, screenshot 3D) vào thư mục:
   - `docs/report/evidence/fit/` (cho kết quả đo đạc hình học)
   - `docs/report/evidence/ai/` (cho biểu đồ huấn luyện và đánh giá model)
