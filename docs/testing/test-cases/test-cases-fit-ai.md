# SỔ NHẬT KÝ CA KIỂM THỬ (TEST CASES LOG)
**Dự án:** Virtual Try-On Platform  
**Tài liệu theo dõi kết quả thực tế:** Toàn bộ thành viên ghi log kiểm thử tại đây.

---

## 1. MẪU TEMPLATE GHI NHẬT KÝ TEST CASE (CHUẨN)

Khi thực hiện kiểm thử cho bất kỳ task nào, copy cấu trúc bảng dưới đây để cập nhật:

```markdown
| Mã Test Case | Module | Cấp độ | Mục tiêu & Dữ liệu Input | Kết quả kỳ vọng (Expected) | Kết quả thực tế (Actual) | Trạng thái (PASS/FAIL) | Link Evidence (Ảnh/Log) | Người test | Ngày thực hiện |
| :--- | :---: | :---: | :--- | :--- | :--- | :---: | :--- | :---: | :---: |
| TC-MOD-XX | M... | Unit/Module | ... | ... | ... | PASS | [evidence_01.png](../../report/evidence/...) | Tên | YYYY-MM-DD |
```

---

## 2. BẢNG THEO DÕI TEST CASES THEO MODULE

### 📐 Module M4 — Fit Engine & AI Models (Owner: M4)

| Mã Test Case | Task liên quan | Cấp độ | Dữ liệu đầu vào (Input) | Kết quả kỳ vọng (Expected Output) | Kết quả thực tế | Trạng thái | Link Evidence | Người test | Ngày |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :---: | :---: |
| **TC-FIT-01** | FIT-01 | Unit | 1) Khối cầu garment nằm ngoài khối cầu body.<br>2) Khối cầu garment nhỏ hơn body (bị xuyên). | 1) Penetration Ratio = 0.<br>2) Ratio khớp giá trị giải tích toán học ($\pm 2\%$). | *Chờ thực hiện* | *Chưa chạy* | - | M4 | - |
| **TC-FIT-02** | FIT-02 | Unit | Vỏ cầu garment cách bề mặt body đúng 2.0 cm. | Khoảng cách trung bình $\approx 2.0 \pm 0.1\text{ cm}$. Mảng `per_vertex_distance` có độ dài đúng bằng số đỉnh mesh. | *Chờ thực hiện* | *Chưa chạy* | - | M4 | - |
| **TC-FIT-03** | FIT-03 | Unit | 1) Garment bao phủ 100% vùng torso.<br>2) Garment bị cắt mất 50% vùng torso. | 1) Coverage $\approx 1.0 \pm 0.05$.<br>2) Coverage $\approx 0.5 \pm 0.05$. | *Chờ thực hiện* | *Chưa chạy* | - | M4 | - |
| **TC-FIT-04** | FIT-04 | Unit | Mesh body + Garment giả lập với khoảng cách từng vùng được định nghĩa trước. | Trả về nhãn từng vùng (*Chest, Waist, Shoulder, Hip*) $\in \{\text{TIGHT, GOOD, LOOSE}\}$ đúng theo ngưỡng cm quy định. | *Chờ thực hiện* | *Chưa chạy* | - | M4 | - |
| **TC-FIT-05** | FIT-05 | Module | Giá trị metrics: $\text{Penetration}=95$, $\text{Distance}=82$, $\text{Coverage}=90$. | $\text{Fit Score} = 0.4(95) + 0.3(82) + 0.3(90) = 89.6\%$. Nhãn tổng thể khớp với phân loại. | *Chờ thực hiện* | *Chưa chạy* | - | M4 | - |
| **TC-FIT-06** | FIT-06 | Unit | Mảng kết quả khoảng cách đỉnh sau tính toán. | Xuất file `heatmap.json` validate $100\%$ theo JSON Schema contract; số phần tử = số đỉnh mesh áo. | *Chờ thực hiện* | *Chưa chạy* | - | M4 | - |
| **TC-AI-01** | AI-01 | Unit | Script sinh dữ liệu Synthetic cho Size Recommendation. | Tạo file CSV không chứa NaN; số đo nằm trong khoảng nhân trắc học hợp lệ; mỗi lớp size ($S, M, L, XL$) chiếm $\ge 10\%$ tổng mẫu. | *Chờ thực hiện* | *Chưa chạy* | - | M4 | - |
| **TC-AI-02** | AI-02 | Module | Vector đặc trưng số đo: chiều cao, ngực, eo, hông, vai + thông số áo từ tập test. | Dự đoán size $\in \{S, M, L, XL\}$; độ tin cậy $\in [0, 1]$; Độ chính xác Accuracy $\ge 85\%$ trên test set synthetic. | *Chờ thực hiện* | *Chưa chạy* | - | M4 | - |
| **TC-AI-03** | AI-03 | Unit | Script sinh dữ liệu Synthetic cho Fit Prediction & Classification. | Features chênh lệch số đo & metrics; Đủ 3 nhãn `Too Tight / Good / Too Loose`, mỗi nhãn chiếm $\ge 15\%$ tổng tập dữ liệu. | *Chờ thực hiện* | *Chưa chạy* | - | M4 | - |
| **TC-AI-04** | AI-04 | Module | Vector đặc trưng fit từ tập kiểm thử độc lập. | Dự đoán Fit Score (MAE $\le 5.0$ điểm) & Phân loại Fit Class (Macro-F1 $\ge 0.75$). | *Chờ thực hiện* | *Chưa chạy* | - | M4 | - |
| **TC-AI-07** | AI-07 | Module | 1) Input hợp lệ.<br>2) Input bị thiếu trường.<br>3) Mô hình AI bị vô hiệu hóa (tắt cờ AI). | 1) Trả về kết quả AI trong $\le 1.0\text{ s}$.<br>2 & 3) Tự động fallback sang tính toán hình học (Geometry Baseline) an toàn, không crash. | *Chờ thực hiện* | *Chưa chạy* | - | M4 | - |

---

### 👤 Module M1 — Body & Measurements (Owner: M1)

| Mã Test Case | Task liên quan | Cấp độ | Dữ liệu đầu vào (Input) | Kết quả kỳ vọng (Expected Output) | Kết quả thực tế | Trạng thái | Link Evidence | Người test | Ngày |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :---: | :---: |
| **TC-BOD-01** | BOD-01 | Unit | 1) Ảnh chân dung toàn thân hợp lệ.<br>2) Ảnh mất chân/đầu, file văn bản txt giả ảnh. | 1) Chuẩn hóa mảng ảnh đúng kích thước.<br>2) Báo lỗi `INVALID_IMAGE` có kiểm soát, không crash. | *Chờ thực hiện* | *Chưa chạy* | - | M1 | - |
| **TC-BOD-03** | BOD-03 | Unit | Bộ 15-20 ảnh test chuẩn + 1 ảnh phong cảnh không người. | Phát hiện đủ 33 keypoints trên $\ge 90\%$ ảnh chuẩn; Ảnh không người trả lỗi `NO_PERSON`. | *Chờ thực hiện* | *Chưa chạy* | - | M1 | - |
| **TC-BOD-04** | BOD-04 | Unit | Vector tham số shape $\beta$ và pose $\theta$ ngẫu nhiên. | Sinh mesh SMPL-X đúng số đỉnh chuẩn ($10.475$ vertices), không chứa tọa độ NaN/Inf; file GLB mở được trên Trimesh & Three.js. | *Chờ thực hiện* | *Chưa chạy* | - | M1 | - |
| **TC-BOD-07** | BOD-07 | Unit | Body mesh fixture 3D chuẩn. | Trích xuất đủ 5 số đo: Chiều cao ($140-210\text{cm}$), Vai ($30-60\text{cm}$), Ngực ($60-140\text{cm}$), Eo ($50-130\text{cm}$), Hông ($70-150\text{cm}$). Sai số cắt lớp $\le 1\text{ cm}$. | *Chờ thực hiện* | *Chưa chạy* | - | M1 | - |
| **TC-BOD-08** | BOD-08 | Module | Toàn bộ bộ ảnh test chụp thật kèm số đo thước dây. | Sai số trung bình (MAE) của Ngực/Eo/Hông so với số đo thật $\le 4.0\text{ cm}$. | *Chờ thực hiện* | *Chưa chạy* | - | M1 | - |

---

### 👕 Module M2 — Garment & Simulation (Owner: M2)

| Mã Test Case | Task liên quan | Cấp độ | Dữ liệu đầu vào (Input) | Kết quả kỳ vọng (Expected Output) | Kết quả thực tế | Trạng thái | Link Evidence | Người test | Ngày |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :---: | :---: |
| **TC-GAR-02** | GAR-02 | Unit | File 3D Mesh T-Shirt mẫu gốc. | Topology sạch, số đỉnh $\le 30.000$, đúng hệ trục tọa độ và đơn vị tiêu chuẩn. | *Chờ thực hiện* | *Chưa chạy* | - | M2 | - |
| **TC-GAR-03** | GAR-03 | Unit | File cấu hình `shirt.json`, `pants.json`. | Load đủ 4 size $S, M, L, XL$; Các thông số kích thước tăng dần đơn điệu $S < M < L < XL$. | *Chờ thực hiện* | *Chưa chạy* | - | M2 | - |
| **TC-GAR-04** | GAR-04 | Module | Mesh gốc + Bảng size chart. | Sinh 4 file mesh tương ứng $S/M/L/XL$; Chu vi ngực đo trên mesh lệch $\le 1.0\text{ cm}$ so với bảng size chart. | *Chờ thực hiện* | *Chưa chạy* | - | M2 | - |
| **TC-GAR-05** | GAR-05 | Module | 3 Body mẫu khác nhau $\times$ Áo T-shirt size M. | Simulation hoàn thành, vải áo ôm ổn định quanh thân người, không rơi tự do, không có đỉnh bị lỗi NaN. | *Chờ thực hiện* | *Chưa chạy* | - | M2 | - |
| **TC-GAR-06** | GAR-06 | Module | Gọi script CLI Draping: `body.obj` + `garment.obj` + `size`. | Xuất file `draped.glb` hợp lệ; Trả về exit code 0; Nếu quá thời gian thì ngắt timeout rõ ràng, không treo máy. | *Chờ thực hiện* | *Chưa chạy* | - | M2 | - |

---

### 🌐 Module M3 — Backend, API & Integration (Owner: M3)

| Mã Test Case | Task liên quan | Cấp độ | Dữ liệu đầu vào (Input) | Kết quả kỳ vọng (Expected Output) | Kết quả thực tế | Trạng thái | Link Evidence | Người test | Ngày |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :---: | :---: |
| **TC-API-01** | API-01 | API | Gửi Request hợp lệ tới toàn bộ Endpoint FastAPI (chế độ Mock). | Trả về HTTP 200/202, cấu trúc JSON response khớp $100\%$ với Pydantic Schema đã quy định. | *Chờ thực hiện* | *Chưa chạy* | - | M3 | - |
| **TC-API-02** | API-02 | API | Gửi dữ liệu sai: thiếu field, file rỗng, sai định dạng size. | Trả về mã lỗi chính xác: HTTP 400/404/422 kèm mã lỗi nội bộ (`error_code`). | *Chờ thực hiện* | *Chưa chạy* | - | M3 | - |
| **TC-API-03** | API-03 | Module | Tạo Job mô phỏng bất đồng bộ qua `/api/tryon/fit`. | Trạng thái chuyển đổi tuần tự: `pending` $\rightarrow$ `running` $\rightarrow$ `completed` (hoặc `failed`). | *Chờ thực hiện* | *Chưa chạy* | - | M3 | - |
| **TC-API-07** | API-07 | Integration | Chuyển đổi cờ cấu hình `APP_MODE = mock` sang `APP_MODE = real`. | Pipeline hoạt động mượt mà ở cả chế độ Mock toàn bộ và chế độ chạy thật từng phần mà không cần sửa code. | *Chờ thực hiện* | *Chưa chạy* | - | M3 | - |

---

### 🖥️ Module M5 — Frontend & 3D WebGL (Owner: M5)

| Mã Test Case | Task liên quan | Cấp độ | Dữ liệu đầu vào (Input) | Kết quả kỳ vọng (Expected Output) | Kết quả thực tế | Trạng thái | Link Evidence | Người test | Ngày |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :---: | :---: |
| **TC-WEB-01** | WEB-01 | Module | Load `body.glb` và `garment.glb` trên Three.js scene. | Hiển thị 3D mượt mà, thao tác xoay (Orbit)/Zoom bình thường, không có lỗi báo đỏ tại Browser Console. | *Chờ thực hiện* | *Chưa chạy* | - | M5 | - |
| **TC-WEB-03** | WEB-03 | Unit | Mock API Client với dữ liệu trả về bị thiếu trường hoặc sai kiểu. | Báo lỗi thân thiện trên giao diện, ứng dụng không bị Crash (màn hình trắng). | *Chờ thực hiện* | *Chưa chạy* | - | M5 | - |
| **TC-WEB-04** | WEB-04 | Module | Dữ liệu phản hồi Fit Result từ Backend. | Bảng hiển thị Fit Score, Region Fit, Size Khuyến nghị hiển thị khớp $100\%$ giá trị trong JSON. | *Chờ thực hiện* | *Chưa chạy* | - | M5 | - |
| **TC-WEB-08** | WEB-08 | Module | File `heatmap.json` chứa mảng khoảng cách từng đỉnh. | Tô màu chuyển sắc chính xác lên bề mặt áo 3D (Đỏ: Chật, Xanh lá: Vừa, Xanh dương: Rộng); Bật/tắt chế độ Heatmap hoạt động tốt. | *Chờ thực hiện* | *Chưa chạy* | - | M5 | - |

---

### 🔗 Chuỗi Test Tích Hợp (Integration: INT-01 $\rightarrow$ INT-07) & E2E

| Mã Test Case | Task | Cấp độ | Phạm vi ghép nối | Tiêu chí đánh giá PASS | Trạng thái |
| :--- | :---: | :---: | :--- | :--- | :---: |
| **TC-INT-01** | INT-01 | E2E | Toàn bộ Mock: Frontend $\leftrightarrow$ Backend Mock $\leftrightarrow$ Mock 3D | Giao diện chạy trọn vẹn từ Upload ảnh giả $\rightarrow$ xem kết quả 3D giả lập trên CI. | *Chờ thực hiện* |
| **TC-INT-02** | INT-02 | Integration | M1 Body thật $\leftrightarrow$ M3 API `/analyze` | Upload ảnh thật $\rightarrow$ sinh ra body mesh và số đo thật đúng schema. | *Chờ thực hiện* |
| **TC-INT-03** | INT-03 | Integration | M2 Simulator thật $\leftrightarrow$ M3 API `/fit` | Chạy Job mô phỏng Blender thật $\rightarrow$ sinh `draped.glb` hiển thị đúng trên Web. | *Chờ thực hiện* |
| **TC-INT-04** | INT-04 | Integration | M4 Fit thật $\leftrightarrow$ M3 API `/fit` | Mesh thật sau simulation được tính toán Fit %, Region Fit và Heatmap chính xác. | *Chờ thực hiện* |
| **TC-INT-05** | INT-05 | E2E | Baseline Real E2E (Ảnh thật $\rightarrow$ Đo đạc $\rightarrow$ Draping $\rightarrow$ Geometry Fit) | Chạy thử nghiệm trên $\ge 10$ ảnh người thật; tỉ lệ thành công $\ge 90\%$. | *Chờ thực hiện* |
| **TC-INT-06** | INT-06 | Integration | M4 AI Size Recommender $\leftrightarrow$ M3 API | Tích hợp model học máy dự đoán Size; tự động fallback về rule-based khi lỗi. | *Chờ thực hiện* |
| **TC-INT-07** | INT-07 | Integration | M4 AI Fit Predictor $\leftrightarrow$ M3 API | Trả về đồng thời điểm Geometry Score và AI Predicted Score. | *Chờ thực hiện* |
