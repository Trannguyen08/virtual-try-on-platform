# CHIẾN LƯỢC KIỂM THỬ (TEST STRATEGY)
**Dự án:** Virtual Try-On Platform  
**Phiên bản:** 1.0  
**Owner phụ trách framework:** M4 (Fit & AI)  
**Áp dụng:** Toàn bộ thành viên nhóm (M1, M2, M3, M4, M5)

---

## 1. MỤC TIÊU & NGUYÊN TẮC KIỂM THỬ

### 1.1. Mục tiêu
- Đảm bảo tính đúng đắn về mặt toán học, hình học 3D và mô hình học máy (AI).
- Đảm bảo các module hoạt động độc lập thông qua Mock và tích hợp mượt mà khi ghép nối thật.
- Thiết lập quy trình kiểm thử tự động (CI) và kiểm thử cục bộ (Evidence Log) minh bạch, có thể tái lập.

### 1.2. Nguyên tắc bất biến (Golden Rules)
1. **Không được ghi chung chung "Testing: Done":** Mọi kiểm thử đều phải có Test Case cụ thể, kèm kết quả `Expected` vs `Actual` và đường dẫn bằng chứng (screenshot, log file, biểu đồ trong `docs/report/evidence/`).
2. **Kiểm thử độc lập với Mock:** Từng module phải pass 100% Unit/Module test trên dữ liệu giả lập (Mock/Fixtures) trước khi yêu cầu tích hợp với module khác.
3. **Phân tách ranh giới CI và Local:**
   - **CI (GitHub Actions):** Chỉ chạy test nhanh (`fast`), dùng Mock hoặc hình học giải tích nhẹ, không tải weights SMPL-X/AI nặng, không chạy Blender headless nặng.
   - **Local / GPU:** Chạy test nặng (`slow`), xuất evidence log để đính kèm vào PR và báo cáo.

---

## 2. KHUNG 7 CẤP ĐỘ KIỂM THỬ (7 TEST LEVELS)

Hệ thống Virtual Try-On áp dụng 7 cấp độ kiểm thử chuẩn hóa:

```
[1. Unit Test] ──► [2. Module Test] ──► [3. Integration Test] ──► [4. API Test]
                                                                        │
[7. User Validation] ◄── [6. Performance Test] ◄── [5. E2E Test] ◄──────┘
```

| Cấp độ | Tên gọi (Level) | Phạm vi & Trọng tâm | Môi trường | Người thực hiện | Tần suất |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **1** | **Unit Test** | Kiểm tra từng hàm, thuật toán toán học, schema, utility, class cô lập. | CI / Local | Từng Owner | Mỗi commit / PR |
| **2** | **Module Test** | Kiểm tra trọn vẹn luồng nội bộ của 1 module với fixture (ví dụ: `OptimizationEstimator`, `Draping CLI`, `FitEvaluator`, `AI Train/Inference`). | Local / CI (nhẹ) | Từng Owner | Trước khi mở PR |
| **3** | **Integration Test** | Kiểm tra giao tiếp giữa 2 hoặc nhiều module (`INT-01` $\rightarrow$ `INT-07`). | Local / CI | M3 phối hợp Owners | Từng mốc Phase 2 |
| **4** | **API Test** | Kiểm tra toàn bộ endpoint FastAPI (`/analyze`, `/garments`, `/fit`, `/jobs`, `/recommend`), validate JSON schema, status code, error codes. | CI / Local | M3 | Mỗi PR Backend |
| **5** | **E2E Test** | Kiểm tra toàn bộ luồng từ Ảnh đầu vào $\rightarrow$ Body 3D $\rightarrow$ Garment $\rightarrow$ Simulation $\rightarrow$ Fit/AI $\rightarrow$ Hiển thị trên 3D Viewer. Có 2 chế độ: `Mock E2E` và `Real E2E`. | CI (Mock) / Local (Real) | M3 + M5 + All | Mốc MS-1, MS-3, MS-4 |
| **6** | **Performance Test** | Đo lường thời gian xử lý (Latency), FPS 3D viewer, bộ nhớ RAM/VRAM, dung lượng model GLB. | Local / Demo machine | M2, M3, M5 | Phase 3 (Hardening) |
| **7** | **User Validation** | Thử nghiệm với 5–10 người thật: chụp ảnh, nhập số đo, kiểm tra độ vừa thực tế so với AI Recommendation. | Thực địa | M1 phối hợp nhóm | Phase 3 (Trước demo) |

---

## 3. CẤU TRÚC PHÂN LOẠI TEST TRONG MÃ NGUỒN

Thư mục kiểm thử `tests/` được tổ chức chặt chẽ tương ứng:

```
tests/
├── conftest.py                   # Global fixtures, mock loaders, pytest config
├── fixtures/                     # Dữ liệu test dùng chung (.glb, .json, mock images)
│
├── unit/                         # Cấp 1: Unit Test từng module
│   ├── body/                     # Test tiền xử lý, đo kích thước
│   ├── garment/                  # Test size chart, mesh generator
│   ├── fit/                      # Test penetration, distance, coverage toán học
│   ├── ai/                       # Test dataset split, model wrapper
│   ├── backend/                  # Test routing, config, schemas
│   └── shared/                   # Test interfaces, utils, mock classes
│
├── integration/                  # Cấp 3: Tích hợp liên module
│   ├── INT-02/                   # Body thật <-> API
│   ├── INT-03/                   # Simulator thật <-> API
│   ├── INT-04/                   # FitEvaluator thật <-> API
│   ├── INT-05/                   # Baseline Real E2E
│   ├── INT-06/                   # AI Size Recommender <-> API
│   └── INT-07/                   # AI Fit Predictor <-> API
│
└── e2e/                          # Cấp 5: End-to-End toàn diện
    ├── mock/                     # E2E chạy hoàn toàn bằng Mock (chạy trong CI)
    └── real/                     # E2E chạy pipeline thật
```

---

## 4. PYTEST MARKERS & CẤU HÌNH THỰC THI

Để tách biệt rõ bài test nhanh cho CI và bài test nặng cho máy cá nhân, hệ thống sử dụng các marker sau trong `pytest`:

- `@pytest.mark.fast` (hoặc test mặc định không gắn nhãn): Test thực thi dưới 2 giây, không tốn tài nguyên.
- `@pytest.mark.slow`: Các bài test mô phỏng Blender, huấn luyện mô hình, load model SMPL-X lớn.
- `@pytest.mark.gpu`: Các bài test yêu cầu CUDA/GPU.
- `@pytest.mark.integration`: Các bài test tích hợp liên module.

### Lệnh chạy tiêu chuẩn:
```bash
# 1. Chạy nhanh cho CI (bỏ qua test nặng):
pytest tests/unit/ -m "not slow and not gpu"

# 2. Chạy toàn bộ Unit test của module Fit & AI:
pytest tests/unit/fit/ tests/unit/ai/

# 3. Chạy kiểm thử tích hợp:
pytest tests/integration/

# 4. Chạy Mock E2E:
pytest tests/e2e/mock/
```

---

## 5. QUY TRÌNH BÁO CÁO & BẰNG CHỨNG (EVIDENCE LOGGING)

Mỗi khi hoàn thành một Task hoặc chạy một đợt test quan trọng:
1. Ghi kết quả vào bảng theo mẫu tại [test-cases.md](virtual-try-on-platform/docs/testing/test-cases.md).
2. Lưu các file minh chứng (ảnh chụp màn hình 3D, biểu đồ Confusion Matrix, log terminal, file JSON đầu ra) vào đúng thư mục:
   - `docs/report/evidence/body/`
   - `docs/report/evidence/garment/`
   - `docs/report/evidence/fit/`
   - `docs/report/evidence/ai/`
   - `docs/report/evidence/backend/`
   - `docs/report/evidence/frontend/`
3. Đính kèm liên kết evidence trong Pull Request trước khi yêu cầu Review.
