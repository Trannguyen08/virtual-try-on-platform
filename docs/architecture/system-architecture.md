# KIẾN TRÚC HỆ THỐNG (SYSTEM ARCHITECTURE)

**Dự án:** Virtual Try-On Platform  
**Tài liệu tổng quan dự án:** [docs/project-overview.md](../project-overview.md)  
**Tài liệu hợp đồng API:** [docs/api/api-contract.md](../api/api-contract.md)  
**Chiến lược kiểm thử:** [docs/testing/test-strategy.md](../testing/test-strategy.md)  

---

## 1. Sơ đồ kiến trúc tổng quan (High-Level Architecture)

```mermaid
flowchart TB
    subgraph ClientLayer ["Client / Presentation Layer"]
        M5["M5: Web Frontend (React + Vite)"]
        Viewer["3D Viewer (Three.js / React Three Fiber)"]
        M5 --- Viewer
    end

    subgraph APILayer ["API & Orchestration Layer (M3)"]
        FastAPI["FastAPI Web Framework"]
        Router["API Routers (/tryon, /jobs, /garments, /assets)"]
        Orchestrator["TryOnOrchestrator"]
        JobMgr["JobManager (In-process Async Queue)"]
        AssetMgr["Asset Static Server"]
        
        FastAPI --> Router
        Router --> Orchestrator
        Orchestrator --> JobMgr
        Router --> AssetMgr
    end

    subgraph ServiceSeam ["Adapter / Seam Interface"]
        Provider["TryOnProvider Protocol"]
        MockProvider["MockProvider (Current MVP)"]
        RealAdapters["Real Adapters (Future)"]
        
        Orchestrator --> Provider
        Provider -.-> MockProvider
        Provider -.-> RealAdapters
    end

    subgraph CoreModules ["Core Domain Modules"]
        M1["M1: Body Estimation & 3D Reconstruction\n(MediaPipe / SMPL-X)"]
        M2["M2: Garment & Cloth Draping\n(Blender / Cloth Simulation)"]
        M4["M4: Fit Evaluation & Size Recommendation\n(Heuristic / AI Predictor)"]
        
        RealAdapters --> M1
        RealAdapters --> M2
        RealAdapters --> M4
    end

    ClientLayer ==>|HTTP / JSON / Multipart| APILayer
    AssetMgr ==>|Binary GLB 2.0 (Y-up, Metres)| Viewer
```

---

## 2. Các ranh giới giao tiếp (System Boundaries & Interfaces)

### 2.1. Frontend (M5) ◄► Backend (M3)
* **Giao thức:** REST API over HTTP/1.1 hoặc HTTP/2.
* **Định dạng dữ liệu:** JSON UTF-8 (tên thuộc tính `snake_case`).
* **Tiêu chuẩn Wire Envelope:**
  * Thành công: `{"data": <payload>, "error": null}`
  * Lỗi: `{"data": null, "error": {"code": "...", "message": "...", "details": []}}`
* **Vòng đời tác vụ bất đồng bộ (Async Job Polling):**
  1. `POST /api/tryon/fit` nhận yêu cầu ➔ trả về `202 Accepted` kèm `job_id` (trạng thái ban đầu: `pending`).
  2. Frontend thực hiện polling `GET /api/jobs/{job_id}` với tần suất ngắn.
  3. Kết quả kết thúc tại `completed` (kèm dữ liệu `FitResult`) hoặc `failed` (kèm `error`).

### 2.2. Backend (M3) ◄► AI & 3D Modules (M1, M2, M4)
Backend giao tiếp với các module thông qua `TryOnProvider` protocol định nghĩa tại [`backend/services/orchestrator.py`](../backend/services/orchestrator.py):

```python
class TryOnProvider(Protocol):
    source: Source

    def garments(self) -> list[GarmentSchema]: ...
    def analyze(self, image: bytes, height_cm: float) -> BodySchema: ...
    def fit(self, body: BodySchema, garment: GarmentSchema, request: FitRequest) -> FitResultSchema: ...
```

* **M1 (Body):** Nhận byte ảnh và chiều cao người dùng (cm). Trả về đối tượng `BodySchema` gồm số đo cơ thể (`height_cm`, `chest_cm`, `waist_cm`, `hip_cm`, `shoulder_width_cm`) và đường dẫn mô hình `BodyMesh` (.glb).
* **M2 (Garment):** Quản lý catalog, cấu trúc size chart chuẩn và chịu trách nhiệm xuất mesh trang phục cũng như mesh trang phục đã draping (`tryon_mesh.glb`).
* **M4 (Fit):** Nhận thông tin số đo cơ thể và bảng size trang phục để đánh giá độ vừa 4 vùng (`chest`, `waist`, `hip`, `shoulder`) theo thang nhãn `tight | good | loose | unknown`, tính toán `fit score` và gợi ý kích cỡ `recommendation.size`.

---

## 3. Quy chuẩn mô hình 3D (3D Mesh Conventions)

Tất cả các tài sản 3D (Asset) được sinh ra từ M1, M2 hoặc phục vụ cho M5 phải tuân thủ chuẩn hình học thống nhất:

| Thuộc tính | Quy định bắt buộc |
| :--- | :--- |
| **Định dạng** | GLB 2.0 (Binary glTF) |
| **Đơn vị kích thước** | Mét (chuyển đổi từ cm chia 100 đúng 1 lần tại adapter) |
| **Hệ tọa độ** | Tay phải (Right-handed): `+Y` lên trên, `+Z` ra trước ngực, `+X` sang trái người mẫu |
| **Gốc tọa độ (Origin)** | Mặt sàn, chính giữa hai bàn chân (`Y = 0`) |
| **Tư thế chuẩn (Pose)** | T-pose: người đứng thẳng, hai chân song song, hai tay dang ngang |
| **Đồng nhất khung nhìn** | Mesh cơ thể và mesh áo draping phải dùng chung một khung tọa độ để không bị lệch tâm khi tải |

---

## 4. Bảo mật & Xử lý tài nguyên (Security & Resource Management)

1. **Bảo vệ chống tấn công Decompression Bomb:**
   Mã nguồn sử dụng thư viện `Pillow` kết hợp `warnings.catch_warnings()` để chặn các file ảnh có kích thước giải nén bất thường (pixel flood) vượt quá 16 triệu điểm ảnh hoặc dung lượng vượt quá 5 MiB.
2. **Kiểm tra loại nội dung thực tế (MIME & Binary Verification):**
   Không tin tưởng phần mở rộng của file (extension) hay header `Content-Type` do client gửi lên; backend trực tiếp giải mã và kiểm tra cấu trúc nhị phân của ảnh (PNG/JPEG) trước khi chuyển vào pipeline xử lý.
3. **Chống tấn công Directory Traversal:**
   Đường dẫn phục vụ file tĩnh `.glb` được kiểm tra chặt chẽ (`resolved path` phải nằm tuyệt đối bên trong thư mục `backend/fixtures/assets/`), chặn mọi ký tự `/`, `\`, `..` hoặc mã hóa URL lậu.
4. **Cấu hình CORS nghiêm ngặt:**
   Chỉ cho phép các Origin chỉ định trong `CORS_ORIGINS` (mặc định các cổng 5173 và 3000 phục vụ dev). Tuyệt đối không dùng ký tự đại diện `*` trong môi trường hỗ trợ xác thực.
