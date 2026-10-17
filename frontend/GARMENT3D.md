# Tạo trang phục 3D trong ứng dụng chính

Trang **Tạo trang phục 3D** nằm trong menu của ứng dụng tại `/garment-3d`.
Đường dẫn cũ `/garment3d.html` chuyển tiếp đến trang này. Giao diện dùng chung
header và footer với các trang còn lại.

Backend chính phục vụ Garment 3D cùng trên cổng 8000. Đặt
`GARMENT3D_PROVIDER=local` trong `.env` ở gốc repo nếu muốn ghi rõ provider mặc định,
cài dependency theo `backend/requirements-dev.txt`, rồi chạy:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --env-file .env --reload --host 127.0.0.1 --port 8000
```

Chạy frontend từ `frontend/`:

```powershell
npm.cmd run dev
```

Trang Garment 3D gọi `/garment3d/...` qua `VITE_API_URL`, mặc định là
`http://localhost:8000` trong chế độ dev. Bản production cần đặt `VITE_API_URL`
đến backend chính đã triển khai.

Trang nhận một đến bốn ảnh của cùng một trang phục và chiều dài thật tùy chọn.
Chiều dài giúp quy đổi pixel sang centimet; nếu thiếu, GLB vẫn xem được nhưng
metadata không đánh dấu `fit_ready`. Bảng size trên trang là tham khảo. Kết quả
hiện chỉ tạo/xem/tải garment GLB; API thử đồ của body chưa nhận GLB này làm
trang phục để mặc lên body.

`npm.cmd run build` tạo một ứng dụng Vite với trang Garment 3D trong cùng luồng.
