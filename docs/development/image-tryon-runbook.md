# Chạy luồng thử đồ từ ảnh trang phục

Luồng `/try-on` dùng body MPFB được tạo trên trang, pipeline local dựng áo từ ảnh
và worker Blender ghép một GLB. Kết quả là cảnh 3D tĩnh. Trang này không tính
điểm fit, khuyến nghị size hay mô phỏng vải.

## Chuẩn bị

1. Dùng Python 3.11 với package trong `backend/requirements.txt` và frontend
   dependencies đã cài sẵn theo hướng dẫn dự án. Cần Blender có add-on MPFB2
   để tạo body, và `BLENDER_PATH` trỏ đúng executable đó.
2. PostgreSQL và thư mục `data/assets/` phải được giữ qua lần khởi động lại.
   `data/assets/` chứa ảnh và GLB người dùng, đã được thêm vào `.gitignore`.
3. Backend và worker phải dùng cùng `DATABASE_URL`, cùng kho `data/assets/` và
   cùng bản mã. Worker không được chạy trên máy khác nếu chưa dùng storage chia sẻ.

Các lệnh dưới đây **dành cho người vận hành tự chạy** trong các terminal riêng:

```powershell
docker compose up -d postgres
python -m alembic upgrade head
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

```powershell
python -m backend.workers.image_tryon
```

```powershell
cd frontend
npm run dev
```

Nếu Blender không có trong `PATH`, đặt `BLENDER_PATH` trong terminal chạy API
**và** worker. API dùng Blender để tạo body; worker dùng Blender để ghép cảnh.

## Thử thủ công

1. Mở `/try-on`, tạo body MPFB từ thông số hoặc nhập ID body MPFB đã tạo. Đợi
   body hoàn tất; đường dẫn tải body phải là `/api/assets/body-<id>.glb`.
2. Tải ảnh áo mặt trước JPG/PNG/WebP, có thể thêm mặt sau và hai bên. Nhập
   chiều dài áo thực tế theo cm rồi tạo cảnh thử đồ.
3. Theo dõi trạng thái job `pending → running → completed`. Khi hoàn tất,
   viewer chỉ tải `/api/assets/tryon-<job_id>.glb` và hiển thị body cùng áo.
4. Tải lại trang và khởi động lại API; body và job hoàn tất phải còn tra cứu
   được. Kiểm tra GLB cuối giữ màu/họa tiết và body không bị thay bằng fixture.
5. Thử body ID sai, ảnh BMP hoặc nội dung ảnh hỏng, thiếu số đo áo, dừng worker
   trong lúc chạy, và ảnh không tách được nền. UI cần hiện mã/lời lỗi rõ ràng.

Không đánh dấu nghiệm thu khi chưa có kết quả PostgreSQL thật, Blender MPFB2,
ảnh áo thực và ảnh chụp viewer. Kiểm thử nhanh cần người vận hành chạy:

```powershell
python -m pytest tests/unit/backend/test_image_tryon.py tests/unit/backend/test_persistence.py -q
```

## Giới hạn hiện tại

- Worker dùng PostgreSQL làm hàng đợi với lease 15 phút; nếu process chết,
  job được thử thêm một lần khi worker khác lấy lại. Lỗi xử lý bình thường
  chuyển `failed` và không tự retry.
- Body được ghép ở tư thế tĩnh; chưa có rig động và chưa chạy cloth simulation.
  `simulate_cloth=true` hiện cho lỗi `SIMULATION_UNAVAILABLE` trong job.
- Fit hình học dùng mốc chiều cao và khoảng hở bề mặt 1 cm. Nếu quá nhiều đỉnh
  áo xuyên sâu vào body, job thất bại thay vì trả GLB không đạt chất lượng.
- Worker chỉ dùng pipeline local parametric. Kết quả từ provider Tripo hoặc
  mock của `/garment3d` chưa được ghép vào luồng này.
- Người dùng chọn `garment_type`; hệ thống chưa tự phân loại loại áo/quần từ ảnh.
  Trường `result.reconstruction` ghi phương pháp tách nền, chuẩn tỉ lệ và mesh.
