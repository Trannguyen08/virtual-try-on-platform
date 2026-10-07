---
name: m4-fit-ai-expert
description: Chuyên môn kỹ thuật, phương pháp luận hình học 3D và kiến trúc AI cho Module M4 (Fit & AI) trong dự án Virtual Try-On Platform.
---

# M4 FIT & AI EXPERT SKILL

## 1. Bản chất Kiến trúc M4 (Hybrid Architecture)
Module M4 không thay thế toàn bộ toán hình học bằng AI, mà áp dụng mô hình **Hybrid thông minh**:

```text
┌─────────────────┐       ┌────────────────────┐
│   3D Body Mesh  │  và   │ Draped Garment Mesh│
└────────┬────────┘       └─────────┬──────────┘
         │                          │
         └────────────┬─────────────┘
                      ▼
        ┌───────────────────────────┐
        │  GEOMETRY FIT EVALUATION  │  <-- Tính toán vật lý chính xác, đáng tin cậy
        │  (Penetration, Dist, Cov) │
        └─────────────┬─────────────┘
                      │
            ┌─────────┴─────────┐
            ▼                   ▼
    ┌───────────────┐   ┌────────────────┐
    │  GEOMETRY     │   │  AI PREDICTOR  │  <-- Học pattern và suy luận siêu nhanh
    │  FIT SCORE    │   │  (ML Models)   │
    │  (Baseline)   │   └───────┬────────┘
    └───────┬───────┘           │
            │                   │ (Nếu AI lỗi hoặc confidence thấp)
            │◄──────────────────┘ [Fallback Mechanism]
            ▼
    ┌────────────────────────────────────┐
    │  FINAL FIT RESULT & SIZE RECOMMEND │
    └────────────────────────────────────┘
```

---

## 2. Phương pháp luận Kỹ thuật theo Từng Phân vùng

### 2.1. Phân hệ Hình học (`fit/`)
- **Triết lý:** Mọi bài toán hình học 3D đều phải có lời giải giải tích (analytical baseline) trước khi lập trình.
- **Tính toán:** Sử dụng `Trimesh` và `NumPy` để tính Signed Distance, Bounding Box, và Cắt lớp (Mesh slicing).
- **Phân tách:** Độc lập với Blender. Toàn bộ logic `fit/` nhận trực tiếp đối tượng Mesh 3D chuẩn hóa (không phụ thuộc vào engine mô phỏng).

### 2.2. Phân hệ Học máy (`ai/`)
- **Chiến lược dữ liệu:**
  - *Giai đoạn 1 (Synthetic v1):* Sinh dữ liệu số đo người theo phân phối chuẩn Gaussian kết hợp bảng Size Chart để huấn luyện sớm Size Recommender.
  - *Giai đoạn 2 (Simulation v2):* Thu thập đặc trưng từ batch simulation thật để tinh chỉnh Fit Predictor.
- **Chiến lược Mô hình hóa:** Bắt đầu từ các mô hình dạng bảng (Tabular) giải thích được: Random Forest $\rightarrow$ XGBoost $\rightarrow$ Multi-Layer Perceptron (MLP). Tuyệt đối không phức tạp hóa bằng Deep Learning cồng kềnh khi dữ liệu chưa đủ lớn.

---

## 3. Tài liệu Tham khảo Chuyên sâu (References)
Khi giải quyết các vấn đề cụ thể, Agent đọc thêm các file trong thư mục `references/`:
- [data-contract.md](references/data-contract.md): Chi tiết JSON Schema đầu vào/đầu ra, bảng đơn vị đo và hệ trục tọa độ.
- [fit-formulas.md](references/fit-formulas.md): Đặc tả các công thức toán học và ngưỡng phân loại Fit đã được project phê duyệt.
- [edge-cases.md](references/edge-cases.md): Cẩm nang xử lý các trường hợp dị biệt: mesh rỗng, mặt hở, điểm NaN, người mẫu ngoại cỡ.
