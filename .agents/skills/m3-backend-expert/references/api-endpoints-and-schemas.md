# REFERENCE: API ENDPOINTS & PYDANTIC SCHEMAS (M3)

Đặc tả chi tiết các RESTful Endpoint của FastAPI, định dạng Request/Response và Pydantic Schemas cho Module M3.

---

## 1. Danh sách Endpoint Chuẩn

### 1.1. `GET /garments`
- **Mục đích:** Trả về danh mục các mẫu trang phục có sẵn kèm bảng size chart.
- **Response 200 OK:**
  ```json
  [
    {
      "garment_id": "tshirt_cotton_01",
      "name": "Classic Cotton T-Shirt",
      "sizes": ["S", "M", "L", "XL"],
      "size_chart": {
        "S": { "chest": 94.0, "length": 66.0 },
        "M": { "chest": 100.0, "length": 68.0 },
        "L": { "chest": 106.0, "length": 70.0 },
        "XL": { "chest": 112.0, "length": 72.0 }
      }
    }
  ]
  ```

### 1.2. `POST /tryon/analyze`
- **Mục đích:** Tải ảnh chân dung người dùng, kích hoạt M1 trích xuất 5 số đo và sinh mesh body.
- **Request (Multipart/form-data):** `image` (file binary), `height` (float, tùy chọn, cm), `gender` (string).
- **Response 200 OK:**
  ```json
  {
    "body_id": "body_usr_9981",
    "measurements": {
      "height": 172.0,
      "shoulder": 44.0,
      "chest": 92.0,
      "waist": 78.0,
      "hip": 94.0
    },
    "mesh_url": "/api/static/bodies/body_usr_9981.glb"
  }
  ```

### 1.3. `POST /tryon/fit` (Async Job)
- **Mục đích:** Kích hoạt thử đồ 3D và tính điểm Fit cho một body và size áo cụ thể.
- **Request (JSON):**
  ```json
  {
    "body_id": "body_usr_9981",
    "garment_id": "tshirt_cotton_01",
    "size": "M"
  }
  ```
- **Response 202 Accepted:**
  ```json
  {
    "job_id": "job_01h8x9p3...",
    "status": "pending",
    "estimated_seconds": 120
  }
  ```

### 1.4. `GET /jobs/{id}`
- **Mục đích:** Kiểm tra trạng thái Job thử đồ.
- **Response 200 OK (khi hoàn thành):**
  ```json
  {
    "job_id": "job_01h8x9p3...",
    "status": "completed",
    "result": {
      "fit_score": 88.5,
      "classification": "Good",
      "draped_mesh_url": "/api/static/draped/job_01h8x9p3.glb",
      "heatmap_url": "/api/static/heatmaps/job_01h8x9p3.json"
    }
  }
  ```
