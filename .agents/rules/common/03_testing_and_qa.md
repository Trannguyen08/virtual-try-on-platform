# RULE 03: TESTING, QA & EVIDENCE LOGGING (COMMON)

> **Phạm vi áp dụng:** Áp dụng bắt buộc cho toàn bộ Agent ở mọi Role (M1, M2, M3, M4, M5).

---

## 1. Tham chiếu Bắt buộc (Mandatory Reference)
Trước khi viết bất kỳ bài test nào, Agent **BẮT BUỘC** phải đối chiếu:
1. `docs/testing/test-strategy.md` (Chiến lược kiểm thử 7 cấp: Unit, Module, Integration, API, E2E, Performance, User Validation).
2. Tài liệu test case liên quan (`docs/testing/test-cases/` hoặc `docs/testing/acceptance-criteria/`).

---

## 2. Quy chuẩn Viết Code Kiểm thử (Test Implementation Standards)

### 2.1. Đặt tên hàm và Định dạng ID Truy vết (Traceability)
Mỗi hàm kiểm thử phải gắn liền với mã Test Case đã định nghĩa:
- Tên hàm chuẩn: `test_<chuc_nang>_tc_<id>()` (chữ thường, gạch dưới).
- Bắt buộc ghi rõ Docstring chuẩn ở đầu hàm test:
```python
def test_garment_size_scaling_tc_gar_04():
    """
    Test Case ID: TC-GAR-04
    Target: Sinh mesh 4 size S/M/L/XL từ mesh gốc theo bảng size chart.
    Expected: Chu vi ngực đo trên mesh lệch <= 1.0 cm so với bảng thông số size.
    """
    # Code test ở đây...
```

### 2.2. So sánh Số thực (Float Approximation)
- Đối với mọi phép so sánh khoảng cách hình học, diện tích, tọa độ đỉnh, **BẮT BUỘC dùng `pytest.approx`**:
```python
assert avg_distance == pytest.approx(0.02, abs=1e-3)  # Đơn vị mét
assert chest_circumference == pytest.approx(96.0, abs=1.0)  # Đơn vị cm
```

### 2.3. Tái lập Kết quả (Seed Fixing)
- Mọi bài test liên quan đến tạo mesh ngẫu nhiên, sinh dữ liệu nhân trắc học, chia tách dữ liệu, huấn luyện AI **bắt buộc phải cố định Random Seed**:
```python
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
```

### 2.4. Kiểm thử Bắt buộc cho Cơ chế Dự phòng (Zero-Crash Fallback)
- Mọi module tích hợp với bên ngoài (API Backend, AI Inference, Simulation CLI, Three.js 3D Viewer) **bắt buộc phải có bài test kiểm tra kịch bản sự cố**:
  - Dữ liệu rỗng, file hỏng, thiếu trường, timeout mô phỏng.
  - Hệ thống phải trả về lỗi có cấu trúc hoặc fallback an toàn, **tuyệt đối không được crash sập server hay vỡ giao diện (Zero Crash)**.

---

## 3. Quy chuẩn Thu thập Bằng chứng Kiểm thử (Evidence Logging)
Sau khi User chạy test có kết quả, Agent hướng dẫn cập nhật bảng Test Case Markdown:
- Cột **Trạng thái**: Ghi `PASS ✅` hoặc `FAIL ❌`.
- Cột **Kết quả thực tế**: Ghi rõ số liệu định lượng (ví dụ: `MAE = 0.042 điểm`, `Accuracy = 99.93%`, `Thời gian simulation = 12.4s`).
- Cột **Link Evidence**: Gắn mã bằng chứng `[evidence-xx]` kèm thông tin chi tiết: câu lệnh đã chạy, ngày test, người test.
- **Quy tắc vàng:** Tuyệt đối không được ghi "Testing: Done" một cách chung chung nếu chưa có kết quả log cụ thể.
