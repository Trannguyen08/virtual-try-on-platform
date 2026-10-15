# Tạo trang phục 3D trong ứng dụng chính

Trang **Tạo trang phục 3D** nằm trong menu của ứng dụng tại `/garment-3d`.
Đường dẫn cũ `/garment3d.html` chuyển tiếp đến trang này. Giao diện dùng chung
header và footer với các trang còn lại.

Backend tạo garment vẫn chạy như một service riêng tại cổng 8001. Đặt
`GARMENT3D_PROVIDER=local` trong `.env` ở gốc repo, cài dependency theo
`backend/garment3d/requirements-dev.txt`, rồi chạy:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.garment3d.app:app --port 8001
```

Chạy frontend từ `frontend/`:

```powershell
npm.cmd run dev
```

Trong chế độ dev, trang Garment 3D gọi `http://localhost:8001` theo mặc định.
Đặt `VITE_GARMENT3D_API_URL` nếu service dùng origin khác. Bản production cần
cấu hình biến này đến service garment đã triển khai; nếu bỏ trống, client dùng
`VITE_API_URL`.

Trang nhận một đến bốn ảnh của cùng một trang phục và chiều dài thật tùy chọn.
Chiều dài giúp quy đổi pixel sang centimet; nếu thiếu, GLB vẫn xem được nhưng
metadata không đánh dấu `fit_ready`. Bảng size trên trang là tham khảo. Kết quả
hiện chỉ tạo/xem/tải garment GLB; API thử đồ của body chưa nhận GLB này làm
trang phục để mặc lên body.

`npm.cmd run build` tạo một ứng dụng Vite với trang Garment 3D trong cùng luồng.
