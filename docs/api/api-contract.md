# API contract — M3 mock MVP v0.1

Quyết định tích hợp do M3 chốt cho giai đoạn này (2026-09-28). M1, M2, M4,
M5 triển khai theo contract này, không cần chờ xác nhận để dùng mock. API hiện
không gọi MediaPipe, SMPL-X, Blender hoặc model AI. `/openapi.json` và `/docs`
được sinh từ schema thật trong `backend/schemas/`.

## 1. Quy ước chung

- Base URL local: `http://localhost:8000`. JSON UTF-8, tên trường snake_case.
- Thành công: `{"data": <payload>, "error": null}`. Lỗi HTTP:
  `{"data": null, "error": {"code": "...", "message": "...", "details": []}}`.
  Ngoại lệ: `/health` giữ nguyên `{"status":"healthy"}`; asset trả binary GLB.
- Trường nullable luôn có mặt với `null`; không dùng `0` thay cho dữ liệu chưa có.
  Request JSON fit không nhận field lạ. ID là chuỗi opaque, phân biệt hoa/thường;
  client chỉ lưu/truyền lại, không tự tạo hay parse ID.
- Body, garment, job, fit, recommendation và từng asset có `source`, `method`,
  `notes`. `source` nhận `mock | module | mixed`: fixture; module thật; hoặc kết quả
  tổng hợp còn chứa thành phần mock. `module` không đồng nghĩa với AI: `method`
  phải mô tả phương pháp thực tế. Adapter sau này giữ nguyên schema và khai báo
  provenance đúng ở từng thành phần; không được đổi mock thành module chỉ vì đổi provider.
- `confidence`: số hữu hạn trong [0,1] hoặc `null`; `score`: số hữu hạn trong
  [0,100] hoặc `null`, là điểm fit chứ không phải xác suất. Mock luôn trả cả hai
  là `null`. Module thật chỉ điền confidence khi có ý nghĩa và phương pháp đánh giá.
- M5 phải hiển thị nhãn demo khi `source=mock/mixed`, hiển thị “chưa có” cho null.
  Mock không phải số đo, khuyến nghị mua hàng hoặc đánh giá độ vừa của người dùng.

## 2. Số đo, mesh và tài sản

**Số đo JSON là cm**. `height_cm` là chiều cao đứng; `chest_cm`, `waist_cm`,
`hip_cm` là chu vi; `shoulder_width_cm` là chiều rộng giữa hai vai. Catalog áo dùng
chu vi ngực/eo/gấu `chest_cm`, `waist_cm`, `hem_cm`, chiều rộng vai và chiều dài
áo từ vai xuống gấu `length_cm`; không phải chiều ngang áo trải phẳng.

**Quyết định mesh MVP bắt buộc cho tích hợp M1/M2** (chưa có module thật để đối chiếu):

- GLB 2.0, đơn vị **mét**, hệ tọa độ tay phải; +Y lên trên, +Z phía trước cơ thể,
  +X về bên trái giải phẫu của người mẫu (bên phải màn hình khi nhìn chính diện).
- Gốc ở sàn, chính giữa hai bàn chân; đáy chân Y=0. T-pose: đứng thẳng, chân song
  song, tay duỗi ngang theo ±X, đầu nhìn +Z. Mesh garment/draped dùng cùng khung
  tọa độ với body, không tự căn giữa từng mesh trong viewer.
- Chuyển cm sang m bằng chia 100 đúng một lần tại adapter xuất mesh. M2 chuyển
  tọa độ native Blender sang khung này khi export; M5 dùng Y-up, không tự xoay lại.
- Fixture là các khối hộp ghép thành người T-pose và áo, **không** tái dựng người,
  không mô phỏng vải, không khớp số đo/size. Chiều cao hình khối cố định 1.72m.
- `Asset = {source, method, notes, format: "glb", url: "/api/assets/<name>.glb"}`.
  `Body.mesh`, `Garment.mesh`, `FitResult.assets.body_mesh/garment_mesh/tryon_mesh`
  đều là `Asset | null`. `tryon_mesh` là scene tổng hợp body + áo; M5 chọn scene
  này **hoặc** hai mesh riêng, không tải cả ba chồng nhau.
- URL tương đối tính từ **backend origin**, ví dụ
  `new URL(asset.url, API_BASE_URL).href`, không tính từ frontend origin.
- Backend chỉ phát URL khi file tồn tại và nằm trong thư mục asset cho phép.
  Hiện chỉ đăng ký `mock-body.glb`, `mock-tshirt.glb`, `mock-tryon.glb`, không có
  file ngoài hay texture từ Internet. Thiếu file => field `null`, GET asset => 404.
  Module thật phải đăng ký asset do backend quản lý trước khi phát URL.
- Tái tạo byte-for-byte: `python scripts/generate_mock_glb.py` (stdlib).
  Fixture đi kèm code; không cần chạy generator để khởi động server.

## 3. Endpoint

| Method/path | Input | Thành công |
| --- | --- | --- |
| `GET /health` | Không | 200, `{"status":"healthy"}` |
| `GET /api/garments` | Không | 200, `data: Garment[]` |
| `POST /api/tryon/analyze` | multipart `image`, `height_cm` | 200, `data: Body` |
| `POST /api/tryon/fit` | JSON `body_id`, `garment_id`, `size` | 202, `data: Job` ở pending |
| `GET /api/jobs/{job_id}` | ID nhận từ fit | 200, `data: Job` |
| `GET /api/assets/{asset_name}` | Tên GLB được đăng ký | 200, `model/gltf-binary` |

### Catalog

Một `demo-tshirt`, `category=t_shirt`, tên `Demo T-shirt (synthetic fixture)`.
`sizes` là danh sách object, không phải danh sách chuỗi; `mesh` là preview chung.

| size | chest_cm | waist_cm | hem_cm | shoulder_width_cm | length_cm |
| --- | ---: | ---: | ---: | ---: | ---: |
| S | 92 | 88 | 92 | 42 | 66 |
| M | 100 | 96 | 100 | 44 | 69 |
| L | 108 | 104 | 108 | 46 | 72 |
| XL | 116 | 112 | 116 | 48 | 75 |

Đây là chart demo, không lấy từ nhà sản xuất. File M2
`garment/size_chart/charts/shirt.json` hiện còn rỗng; mock dùng
`backend/fixtures/catalog.json` để không giả định M2 đã triển khai.

### Analyze

`Content-Type: multipart/form-data`. Field `image` là file PNG/JPEG hợp lệ có
MIME tương ứng `image/png`/`image/jpeg`, không quá 5 MiB (5×1024×1024 bytes),
không quá 16 triệu pixel. Backend kiểm tra định dạng thật, verify và decode;
không tin extension hay MIME đơn thuần. `height_cm` là số hữu hạn từ **140 đến 210**
(bao gồm hai đầu), chọn theo dải chiều cao trong tài liệu kiểm thử hiện có.
Không kiểm tra có người/toàn thân/tư thế, không sinh `NO_PERSON` trong mock.
Ảnh không được lưu xuống disk bởi ứng dụng hoặc giữ lại trong body/job store.
Multipart parser có thể dùng file tạm và giới hạn kích thước được kiểm tra sau
khi parse; deployment sau này cần giới hạn request tại proxy nếu mở ra Internet.

Ví dụ request (CMD hoặc PowerShell, sử dụng `curl.exe`):

```text
curl.exe -X POST http://localhost:8000/api/tryon/analyze -F "image=@C:\images\person.jpg;type=image/jpeg" -F "height_cm=170"
```

Response 200 (ID trong ví dụ chỉ minh họa; dùng ID thực khi gọi fit):

```json
{
  "data": {
    "source": "mock",
    "method": "fixed_demo_measurements",
    "notes": [
      "height_cm is user supplied; other measurements are fixed synthetic fixtures.",
      "No person detection, image-based measurement, or AI inference is performed."
    ],
    "body_id": "body_example",
    "measurements": {"height_cm": 170, "chest_cm": 96, "waist_cm": 80, "hip_cm": 98, "shoulder_width_cm": 44},
    "confidence": null,
    "mesh": {
      "source": "mock", "method": "box_geometry_fixture", "format": "glb",
      "url": "/api/assets/mock-body.glb",
      "notes": [
        "Synthetic boxes for viewer integration only; not a reconstructed or draped mesh.",
        "Geometry is fixed and does not represent measurements or selected size."
      ]
    }
  },
  "error": null
}
```

`height_cm` chỉ echo giá trị do người dùng khai báo. Bốn số đo còn lại cố định cho
mọi ảnh/chiều cao; chúng **không được tính từ ảnh hoặc suy ra từ chiều cao**.
Mỗi analyze thành công tạo body ID mới, lưu process-local.

### Fit và job

Request JSON:

```json
{"body_id":"body_example","garment_id":"demo-tshirt","size":"M"}
```

Size phân biệt hoa/thường, nhận S/M/L/XL và phải tồn tại trong chart garment.
Body phải được tạo bởi analyze trên cùng server process. Sai input không tạo job.
Response 202:

```json
{
  "data": {
    "source": "mock", "method": "in_process_job",
    "notes": ["In-memory job; discarded on server restart."],
    "job_id": "job_example", "status": "pending",
    "request": {"body_id":"body_example","garment_id":"demo-tshirt","size":"M"},
    "result": null, "error": null
  },
  "error": null
}
```

State machine: `pending -> running -> completed | failed`. Không sleep giả,
không retry/cancel/progress phần trăm; POST lặp tạo job mới. `BackgroundTasks`
chạy sau khi trả response. Mock nhanh nên có thể không quan sát được running
khi poll; `pending` trong response tạo job là snapshot không thay đổi.

| Job.status | Job.result | Job.error | HTTP khi GET job |
| --- | --- | --- | --- |
| pending | null | null | 200 |
| running | null | null | 200 |
| completed | FitResult | null | 200 |
| failed | null | Error | 200 |

Running response giữ đủ mọi field như pending, chỉ thay `status` thành `running`.
`request` luôn là input đã chấp nhận. GET thành công có `error` ngoài cùng là null,
kể cả job failed; lỗi xử lý ở `data.error`. Job không tồn tại trả HTTP 404.

`data.result` của completed có cấu trúc đầy đủ như ví dụ sau (nằm trong Job ở trên):

```json
{
  "source": "mock", "method": "fixed_demo_fit",
  "notes": ["Labels are scripted by size for UI testing; not an actual fit evaluation."],
  "body_id": "body_example", "garment_id": "demo-tshirt", "size": "M",
  "recommendation": {
    "source": "mock", "method": "fixed_demo_recommendation",
    "notes": ["Always M for the demo; not a personalized recommendation."],
    "size": "M", "confidence": null
  },
  "overall": {
    "source": "mock", "method": "fixed_demo_fit",
    "notes": ["Labels are scripted by size for UI testing; not an actual fit evaluation."],
    "score": null, "label": "good", "confidence": null
  },
  "regions": [
    {"region":"chest","source":"mock","method":"fixed_demo_fit","notes":["Labels are scripted by size for UI testing; not an actual fit evaluation."],"score":null,"label":"good","confidence":null},
    {"region":"waist","source":"mock","method":"fixed_demo_fit","notes":["Labels are scripted by size for UI testing; not an actual fit evaluation."],"score":null,"label":"good","confidence":null},
    {"region":"hip","source":"mock","method":"fixed_demo_fit","notes":["Labels are scripted by size for UI testing; not an actual fit evaluation."],"score":null,"label":"good","confidence":null},
    {"region":"shoulder","source":"mock","method":"fixed_demo_fit","notes":["Labels are scripted by size for UI testing; not an actual fit evaluation."],"score":null,"label":"good","confidence":null}
  ],
  "assets": {
    "body_mesh": {"source":"mock","method":"box_geometry_fixture","notes":["Synthetic boxes for viewer integration only; not a reconstructed or draped mesh.","Geometry is fixed and does not represent measurements or selected size."],"format":"glb","url":"/api/assets/mock-body.glb"},
    "garment_mesh": {"source":"mock","method":"box_geometry_fixture","notes":["Synthetic boxes for viewer integration only; not a reconstructed or draped mesh.","Geometry is fixed and does not represent measurements or selected size."],"format":"glb","url":"/api/assets/mock-tshirt.glb"},
    "tryon_mesh": {"source":"mock","method":"box_geometry_fixture","notes":["Synthetic boxes for viewer integration only; not a reconstructed or draped mesh.","Geometry is fixed and does not represent measurements or selected size."],"format":"glb","url":"/api/assets/mock-tryon.glb"}
  }
}
```

Mock luôn recommend M, size S có label tight, M good, L/XL loose; mọi vùng nhận
cùng label demo. Enum chung `tight | good | loose | unknown`; vùng chuẩn
`chest | waist | hip | shoulder`, client map theo `region`, không theo index.
Module thật trả `unknown`/null nếu không đánh giá được vùng; recommendation.size
có thể null nếu chưa khuyến nghị được. Không có heatmap/per-vertex metric trong MVP;
đây là hạng mục bổ sung sau, không ngụ ý đã đáp ứng FIT-06/AI-07 của tài liệu M4.

Failed response (test thay provider để gây lỗi; không có endpoint cố tình làm job fail):

```json
{
  "data": {
    "source": "mock", "method": "in_process_job",
    "notes": ["In-memory job; discarded on server restart."],
    "job_id": "job_example", "status": "failed",
    "request": {"body_id":"body_example","garment_id":"demo-tshirt","size":"M"},
    "result": null,
    "error": {"code":"PROCESSING_FAILED","message":"Try-on processing failed","details":[]}
  },
  "error": null
}
```

## 4. Lỗi

| HTTP | code | Điều kiện |
| --- | --- | --- |
| 400 | INVALID_IMAGE | Rỗng, hỏng, giả ảnh hoặc nội dung khác MIME |
| 413 | IMAGE_TOO_LARGE | Quá 5 MiB hoặc quá giới hạn pixel |
| 415 | UNSUPPORTED_IMAGE_TYPE | MIME khác PNG/JPEG |
| 422 | VALIDATION_ERROR | Thiếu field, JSON hỏng, chiều cao ngoài dải, size sai enum, field JSON fit lạ |
| 422 | SIZE_NOT_AVAILABLE | Size thuộc enum nhưng garment không hỗ trợ |
| 404 | BODY_NOT_FOUND / GARMENT_NOT_FOUND / JOB_NOT_FOUND | ID không tồn tại |
| 404 | ASSET_NOT_FOUND | Asset chưa đăng ký, thiếu file hoặc đường dẫn không an toàn |
| 404 | NOT_FOUND | Route không tồn tại |
| 500 | INTERNAL_ERROR | Lỗi API không dự kiến; không lộ nội bộ |
| 200 (job failed) | PROCESSING_FAILED | Lỗi provider trong background, nằm ở data.error |

HTTP error khác do framework dùng `HTTP_ERROR`. CORS preflight do middleware xử
lý riêng, không dùng JSON envelope. `details` là danh sách `{field, message}`,
rỗng với lỗi nghiệp vụ; validation dùng field path như `body.height_cm`.
Client xử lý theo code/status, không so khớp message vốn có thể đổi theo thư viện.

Ví dụ request `{"body_id":"missing","garment_id":"demo-tshirt","size":"M"}`
trả 404:

```json
{"data":null,"error":{"code":"BODY_NOT_FOUND","message":"Body not found; submit analyze again","details":[]}}
```

## 5. Vận hành và bàn giao module

- Một process/worker, không DB/Redis/Celery/tài khoản. Restart hoặc reload làm mất
  toàn bộ body/job; khi nhận 404, M5 chạy analyze rồi fit lại. Store chưa có TTL,
  chỉ phục vụ local MVP, không phù hợp chạy dài hạn hay chia nhiều workers.
- CORS mặc định chỉ localhost/127.0.0.1 cổng 5173 và 3000; không credentials,
  chỉ GET/POST, header Content-Type. Biến môi trường `CORS_ORIGINS` là danh sách
  origin phân tách bằng dấu phẩy; không wildcard. Vite đổi port thì cấu hình lại.
- `TryOnProvider` ở `backend/services/orchestrator.py` định nghĩa ranh giới typed:
  `garments() -> list[GarmentSchema]`, `analyze(image: bytes, height_cm: float) -> BodySchema`,
  `fit(body, garment, request) -> FitResultSchema`. `create_app(provider=...)` là
  seam tích hợp/test. Runtime hiện chỉ dùng MockProvider; chưa có chế độ real khả dụng.
- **M1 nhận:** field số đo, dải chiều cao, byte ảnh đã validate, mesh frame/T-pose;
  trả body ID, measurements, provenance, confidence có ý nghĩa hoặc null và asset đã đăng ký.
- **M2 nhận:** garment ID/chart S–XL, body cùng hệ trục/đơn vị, requested size;
  cung cấp catalog và GLB garment/draped. Không trả đường dẫn disk ra API.
- **M4 nhận:** body/garment, size, mesh đã chuẩn hóa; trả recommendation, overall,
  bốn vùng cùng enum lower-case, score/confidence/provenance. Adapter map nhãn
  TIGHT/GOOD/LOOSE trong tài liệu cũ sang tight/good/loose của API.
- **M5 nhận:** base URL, multipart analyze, envelope, polling state machine,
  URL asset theo backend origin, null/source semantics. Gửi FormData không tự
  đặt Content-Type để browser thêm boundary; dừng poll ở completed/failed,
  có timeout phía UI; server chưa có timeout/cancel job.
- `shared/interfaces/*` vẫn là placeholder của repo. Contract MVP đã thực thi
  tại backend schemas/provider, không coi các interface rỗng là module đã sẵn sàng.
- Type frontend cũ `error?: string` không khớp lỗi object nên chỉ cập nhật
  `frontend/src/api/types.ts` cho envelope; không xây client, hooks hay giao diện.
- Thay từng provider không đổi field/schema frontend. Thay đổi phá vỡ contract
  cần version mới; không lén đổi đơn vị, nghĩa score, hay enum.
