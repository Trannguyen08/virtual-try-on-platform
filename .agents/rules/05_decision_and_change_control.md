# RULE 05: DECISION & CHANGE CONTROL (KIỂM SOÁT THAY ĐỔI)

## 1. Nguyên tắc "Contract First" (Hợp đồng là Tối thượng)
Agent tuyệt đối không viết code dựa trên suy đoán về dữ liệu của module khác. Quy trình xử lý dữ liệu của M4 luôn tuân thủ:

```text
Input Schema Validation → Core Processing → Output Schema Validation
```

- Khi M1, M2 chưa có output thật: M4 dùng **Mock Contract** để viết Unit Test và hoàn thiện toàn bộ thuật toán.
- Khi có output thật từ M1, M2: M4 chạy **Contract Validation**. Nếu dữ liệu sai khác schema, M4 báo lỗi ngay ở lớp Validation, **tuyệt đối không Silent Fix (không âm thầm sửa code M4 để thỏa hiệp với lỗi của module khác)**.

---

## 2. Tiêu chuẩn Đơn vị & Hệ trục Tọa độ Nội bộ (Unit & Coordinates)
Mọi phép tính toán học và hình học 3D trong M4 bắt buộc phải tuân theo hệ quy chiếu chuẩn sau:

| Thuộc tính | Quy định Nội bộ (Internal Standard) | Quy định Ngoại vi (Display / API) | Quy tắc chuyển đổi |
| :--- | :--- | :--- | :--- |
| **Đơn vị đo dài (Length/Distance)** | **Mét (m)** | **Centimet (cm)** | $1\text{ m} = 100\text{ cm}$ |
| **Hệ tọa độ (Coordinate System)** | **Right-handed (Tay phải)** | **Right-handed** | Đồng bộ Three.js |
| **Trục đứng (Up-Axis)** | **Y-up** (Theo chuẩn SMPL-X) | **Y-up** | Giữ nguyên |
| **Trục nhìn (Forward-Axis)** | **+Z forward** | **+Z forward** | Giữ nguyên |

*Cấm tuyệt đối mọi phép tính cộng/trừ/khoảng cách giữa các vector nếu chưa chuẩn hóa về cùng đơn vị (m) và hệ trục (Y-up).*

---

## 3. Khóa Quyết định Cơ sở (Frozen Baseline Decisions)
Các thông số kỹ thuật cốt lõi sau đã được phê duyệt làm Baseline cho dự án. Agent **KHÔNG ĐƯỢC TỰ Ý THAY ĐỔI**:
1. **Công thức Fit Score Baseline:**
   $$\text{Fit Score} = 0.4 \times \text{Penetration} + 0.3 \times \text{Distance} + 0.3 \times \text{Coverage}$$
   *Lưu ý:* Công thức này được quản lý như một phiên bản cấu hình (`FIT_SCORE_CONFIG_V1`) và có **nguồn duy nhất (Single Source of Truth)** từ hằng số trong code (`fit/score/fit_score.py`).
2. **Ngưỡng phân loại Vùng (Region Thresholds):** Ngưỡng phân chia `TIGHT`, `GOOD`, `LOOSE` theo khoảng cách cm.
3. **Mục tiêu AI:** Size Recommender (Phân loại Size), Fit Predictor (Hồi quy điểm Fit Score), Fit Classifier (Phân lớp độ vừa).

---

## 4. Quy trình Thay đổi Quyết định (Change Control Process)
Nếu trong quá trình làm việc, Agent phát hiện công thức, ngưỡng hoặc schema có điểm bất hợp lý cần cải tiến, Agent **BẮT BUỘC** phải tuân theo luồng sau:

```text
Vấn đề (Problem)
  ↓
Phân tích ảnh hưởng (Impact Analysis tới M3, M5)
  ↓
Đề xuất giải pháp (Proposed Change)
  ↓
User phê duyệt (User Approval)
  ↓
Triển khai Code (Implementation)
  ↓
Cập nhật Regression Tests & Chạy kiểm thử
  ↓
Cập nhật Tài liệu (Documentation)
```

---

## 5. Chiến lược Phát triển & Tái lập Kết quả AI (AI Reproducibility)
1. **Không triển khai ồ ạt:** Không viết đồng thời nhiều model phức tạp khi chưa có cơ sở. Tuân thủ luồng:
   ```text
   Baseline (Rule-based) → Candidate Models (RF, XGBoost, MLP) → Evaluation → Lựa chọn theo Evidence → Inference Contract
   ```
2. **Quy chuẩn Tái lập Kết quả (Reproducibility):** Mỗi lần huấn luyện mô hình, bắt buộc phải ghi nhận vào log/evidence:
   - Dataset version & số lượng mẫu (sample count).
   - Tỷ lệ phân chia Train / Val / Test.
   - Cố định Random Seed (`seed=42`).
   - Danh sách Hyperparameters và các chỉ số đo lường (Metrics).

---

## 6. Tiêu chuẩn Hoàn thành Task của M4 (Definition of Done - DoD)
Một task của Module M4 chỉ được coi là hoàn thành khi thỏa mãn đầy đủ 7 tiêu chí:
1. [ ] Code hoàn thiện, sạch sẽ, có Type hints và Docstrings giải thích rõ ràng.
2. [ ] 100% Unit Test liên quan đạt trạng thái **PASS**.
3. [ ] Các test case đều có mã ID truy vết khớp với tài liệu (`TC-FIT-xx`, `TC-AI-xx`).
4. [ ] Cơ chế Fallback sang Geometry được kiểm thử thành công (Zero crash).
5. [ ] Không vi phạm quy tắc `.gitignore` (không stage nhầm file weights, data lớn).
6. [ ] Cập nhật kết quả vào bảng nhật ký `docs/testing/test-cases/test-cases-fit-ai.md`.
7. [ ] Lưu trữ đầy đủ biểu đồ, số liệu minh chứng vào `docs/report/evidence/`.
