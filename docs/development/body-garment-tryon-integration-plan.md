# Kế hoạch xử lý ảnh quần áo thành cảnh thử đồ 3D

> **Trạng thái:** Đã thêm luồng mã v0.2 ở [API contract](../api/api-contract.md); chưa nghiệm thu với PostgreSQL và Blender thật. `/api/tryon/analyze` mock vẫn chỉ nhận PNG/JPEG. Luồng mới `/api/tryon/image-jobs` nhận ảnh trang phục JPG/PNG/WebP và body MPFB đã tạo.

## Mục tiêu và điều kiện đầu vào

Người dùng tải ảnh quần áo lên, hệ thống dựng áo 3D từ ảnh, mặc áo lên **body MPFB đã tạo sẵn**, rồi trả một GLB tổng hợp để xem trong Three.js. Trước khi tạo job, hệ thống cần xác định đúng body MPFB được chọn và có thể truy xuất asset của body đó; tên trường tham chiếu body sẽ được chốt trong contract.

Ảnh quần áo là nguồn cho hình dạng và bề mặt áo. Body MPFB là đầu vào có sẵn của bước ghép trong Blender, không được tạo lại từ ảnh quần áo. Nếu không tìm thấy body hoặc asset không hợp lệ, trả lỗi rõ ràng thay vì dùng body/áo mẫu thay thế.

## Quy trình xử lý hoàn chỉnh

### 1. Frontend — Upload ảnh quần áo

- Người dùng chọn ảnh **JPG, PNG hoặc WebP** và body MPFB đã tạo trước đó.
- Frontend gửi ảnh cùng tham chiếu body lên backend, hiển thị lỗi đầu vào và trạng thái upload. Không coi phần mở rộng file là bằng chứng định dạng ảnh.
- **Đầu ra:** yêu cầu tạo thử đồ chứa ảnh quần áo và tham chiếu body đã chọn.

### 2. Backend FastAPI — Validate, lưu ảnh và đưa job vào queue

- Backend kiểm tra định dạng thực, khả năng giải mã, giới hạn kích thước/pixel và tham chiếu body theo contract mới. Cần bổ sung WebP vào validation của luồng upload quần áo; giới hạn cụ thể phải được chốt trước khi code.
- Sau khi validate, backend **lưu ảnh**, tạo **Job ID**, lưu trạng thái `pending`, rồi đưa công việc vào **queue** cho worker. Không trả thành công nếu ảnh hoặc job chưa lưu được, hoặc việc đưa vào queue thất bại.
- Backend trả Job ID để frontend theo dõi trạng thái `pending → running → completed | failed`. Job và asset cần truy xuất được sau khi tiến trình API khởi động lại.
- **Đầu ra:** ảnh nguồn đã lưu, Job ID và thông điệp trong queue.

### 3. AI Image Processing — Phân tích ảnh quần áo

- Worker đọc ảnh nguồn, **tách nền**, **phân loại loại trang phục**, rồi nhận dạng **kiểu dáng và đặc điểm** cần cho dựng hình, chẳng hạn cổ áo, tay áo, chiều dài, màu và họa tiết khi có thể quan sát được.
- Ghi phương pháp, mức tin cậy nếu có căn cứ và các đặc điểm không xác định được. Ảnh không có quần áo phù hợp hoặc tách nền thất bại phải chuyển job sang `failed` với lỗi có cấu trúc.
- **Đầu ra:** vùng áo đã tách nền và bộ đặc điểm có thể truy vết về ảnh nguồn.

### 4. Garment Reconstruction Service — Dựng mesh áo 3D

- Dựa trên loại/kiểu dáng đã nhận dạng, chọn **template 3D** phù hợp.
- Biến đổi mesh theo đặc điểm quan sát được từ ảnh để tạo hình dạng áo; ghi rõ phần nào suy từ ảnh, phần nào là giả định của template. Không suy ra kích thước cơ thể hoặc độ vừa từ một ảnh quần áo nếu thiếu dữ liệu.
- **Đầu ra:** mesh áo 3D và thông tin template/phép biến đổi để bước sau có thể tái tạo kết quả.

### 5. Texture Processing — Tạo bề mặt áo

- Trích màu và họa tiết từ ảnh để **tạo texture**, gán **UV mapping** lên mesh và thiết lập **vật liệu PBR cơ bản**.
- Kiểm tra UV, texture và material được giữ khi chuyển mesh sang Blender và khi xuất GLB; vùng ảnh không quan sát được phải được xử lý theo quy tắc đã chốt, không tự khẳng định là chi tiết thật.
- **Đầu ra:** mesh áo có UV, texture và material phù hợp để import vào Blender.

### 6. MPFB + Blender Python — Mặc áo lên body

- Nạp **body MPFB đã tạo sẵn** theo tham chiếu của job, sau đó import mesh áo 3D cùng texture và material.
- Kiểm tra body và áo theo cùng chuẩn GLB/mesh: **mét**, hệ tay phải, **Y-up, +Z forward** và cùng gốc/tư thế. Sai chuẩn phải báo lỗi ở ranh giới tích hợp, không âm thầm xoay hoặc co giãn để che lỗi.
- Fit áo lên body bằng các mốc hình học đã chốt, thực hiện **rigging** để áo đi theo body khi cần. Kiểm tra vùng **xuyên mesh**; chỉ chạy **mô phỏng vải khi được bật** và có cấu hình/tài nguyên phù hợp. Ghi rõ mô phỏng có chạy hay không trong kết quả job.
- **Đầu ra:** cảnh Blender gồm body MPFB và áo đã được đặt, rig và kiểm tra hình học.

### 7. Blender Python — Export GLB

- Xuất một GLB chứa **body, clothes, materials và rig nếu có**. Texture phải được đóng gói hoặc tham chiếu theo cách GLB có thể tải độc lập.
- Kiểm tra GLB mở được, đúng hệ tọa độ/tỉ lệ, không mất texture và không có vùng xuyên mesh nghiêm trọng theo tiêu chí nghiệm thu đã chốt.
- **Đầu ra:** file GLB tổng hợp của người mặc áo 3D.

### 8. Backend → Frontend — Lưu GLB và hiển thị

- Backend lưu GLB vào kho asset được quản lý, đăng ký URL an toàn, cập nhật job thành `completed` và trả **URL GLB**. Nếu xử lý lỗi, cập nhật `failed` kèm mã lỗi; không trả URL tới file chưa tồn tại.
- Frontend theo dõi job bằng Job ID, lấy URL khi hoàn tất và dùng **Three.js** để hiển thị người mặc áo 3D. URL tương đối phải được ghép với backend origin. Viewer chỉ tải GLB tổng hợp cho cảnh này để tránh render body/áo hai lần.
- **Đầu ra:** người dùng xem được body MPFB mặc áo dựng từ ảnh, gồm hình dạng và vật liệu đã xuất.

## Hợp đồng và trách nhiệm cần chốt trước khi triển khai

| Phần | Owner chính | Điểm cần chốt |
| --- | --- | --- |
| Upload, job, queue, lưu ảnh/GLB và URL asset | M3 | Endpoint, tên trường body/job, định dạng lỗi, giới hạn ảnh, lưu trữ bền vững và retry/timeout. |
| Tách nền, phân loại, dựng mesh, texture/UV/PBR | M2 và owner AI xử lý ảnh | Schema đặc điểm, template, nguồn/độ tin cậy và điều kiện lỗi. |
| Body MPFB đầu vào | M1 | Asset, tư thế, rig, mốc hình học, đơn vị và hệ trục bàn giao cho Blender. |
| Fit hình học, rigging, mô phỏng tùy chọn và export | M2, phối hợp M1/M3 | Quy tắc căn chỉnh, ngưỡng xuyên mesh, điều kiện mô phỏng, nội dung GLB. |
| Upload, polling và Three.js viewer | M5 | Cách chọn body, trạng thái job, URL asset và hiển thị lỗi. |

M4 chỉ tham gia nếu bổ sung đánh giá độ vừa/size bằng chỉ số hoặc model riêng; việc kiểm tra xuyên mesh ở bước 6 là kiểm tra chất lượng hình học của kết quả Blender. Mọi thay đổi endpoint hoặc schema cần được M3 cập nhật vào API contract trước khi code tích hợp.

## Tiêu chí nghiệm thu đầu cuối

- [ ] Upload một ảnh JPG, PNG hoặc WebP hợp lệ với body MPFB có sẵn tạo được Job ID và job đi qua queue tới worker.
- [ ] Worker tạo được mesh áo và texture từ chính ảnh đã upload; template, phương pháp và các giới hạn được ghi lại.
- [ ] Blender import đúng body/áo, fit và rig theo contract, kiểm tra xuyên mesh; trạng thái mô phỏng vải được ghi rõ.
- [ ] GLB cuối chứa body, áo, material và rig nếu có; Three.js tải từ URL backend và hiển thị đúng tỉ lệ, màu/họa tiết.
- [ ] Ảnh sai định dạng, thiếu body, xử lý thất bại hoặc GLB lỗi trả trạng thái/lỗi rõ ràng; job và asset hoàn tất vẫn tra cứu được sau khi API khởi động lại.

## Triển khai v0.2 và giới hạn đã công bố

- Body MPFB mới tạo được đăng ký vào PostgreSQL và kho `data/assets/`; `body_id`
  là ID job tạo body. Body hoàn tất có thể tra lại bằng
  `GET /api/body-builder/bodies/{body_id}` sau khi API khởi động lại.
- Ảnh áo và job được lưu cùng giao dịch metadata; worker PostgreSQL riêng dùng
  pipeline local parametric của M2 và Blender để ghép cảnh tĩnh. Mô phỏng vải
  chưa được hiệu chuẩn; nếu yêu cầu bật, job trả `SIMULATION_UNAVAILABLE`.
- Bước ghép dùng chiều dài áo thật để chuẩn tỉ lệ, đặt áo theo mốc chiều cao
  body, điều chỉnh khoảng hở bề mặt 1 cm và kiểm tra xuyên mesh. Đây là kết
  quả xem trước hình học, không phải đánh giá fit hoặc gợi ý size.
- Frontend route `/try-on` hiện gọi luồng mới, không tự thay kết quả API lỗi bằng
  mock. Viewer tải một GLB tổng hợp. Các ô nghiệm thu trên chỉ đánh dấu sau khi
  người dùng chạy thử với PostgreSQL, Blender/MPFB2 và ảnh thực tế.
- v0.2 dùng loại trang phục do người dùng chọn, chưa tự phân loại từ ảnh;
  `result.reconstruction` lưu phương pháp tách nền, cách chuẩn tỉ lệ và thông tin
  mesh để truy vết. GLB là tư thế tĩnh, chưa có rig hay mô phỏng vải.
