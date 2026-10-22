# Tích hợp trang Garment 3D vào ứng dụng chính

- Thời điểm: 2026-10-15 10:12 Asia/Saigon.
- Vai trò: M5; M3 sở hữu service garment đang chạy riêng, M2 sở hữu GLB/metadata.
- Mục đích: đưa trang tạo garment từ entrypoint riêng vào menu và shell của frontend hiện có.

## File thay đổi trước → sau

| File | Trước → sau |
| --- | --- |
| `frontend/src/App.tsx` | Tab nội bộ không có Garment 3D → có tab `/garment-3d`, điều hướng bằng History API, tải `Garment3DPage` khi cần và dùng chung header/footer. |
| `frontend/src/components/common/Navbar.tsx` | Menu không có Garment 3D, ẩn toàn bộ điều hướng ở màn hình nhỏ → có mục tạo trang phục và nút mở menu trên màn hình nhỏ; brand dùng button. |
| `frontend/src/styles/home.css` | Navbar chưa có menu thu gọn → thêm kiểu menu responsive và ngưỡng 1199 px để nhãn không xuống dòng. |
| `frontend/src/pages/Garment3DPage.tsx` | Root là `<main>` độc lập và chỉ export named component → root là `<div>` để đặt trong `<main>` của App, thêm default export để lazy import; nhãn hero mô tả Garment 3D. |
| `frontend/src/styles/garment3d.css` | Quy tắc `:root`, `body`, `*` ảnh hưởng toàn trang → giới hạn trong `.g3d-app`, thêm nền và khoảng cách cho trang tích hợp. |
| `frontend/src/api/garment3d.ts` | Mặc định gọi `VITE_API_URL` khi thiếu biến riêng → dev mặc định gọi service garment cổng 8001; production vẫn dùng biến riêng hoặc `VITE_API_URL`. |
| `frontend/src/components/GarmentGenerationProgress.tsx` | Cảnh báo một ảnh nói AI suy đoán → nói các mặt còn lại được ước lượng từ ảnh mặt trước. |
| `frontend/package.json` | Build multi-page bằng config riêng → build Vite một ứng dụng chính. |
| `frontend/garment3d.html` | HTML entrypoint độc lập → xóa. |
| `frontend/src/garment3d-main.tsx` | React root riêng → xóa. |
| `frontend/vite.garment3d.config.ts` | Cấu hình multi-page → xóa. |
| `frontend/public/garment3d.html` | Chưa tồn tại → file chuyển tiếp URL cũ sang `/garment-3d`. |
| `frontend/GARMENT3D.md` | Hướng dẫn trang độc lập → hướng dẫn truy cập trang trong ứng dụng và service cổng 8001. |
| `docs/development/run-backend-frontend.md` | Chỉ mô tả backend chính và frontend → thêm terminal cho service Garment 3D và đường dẫn trang mới. |

## Ảnh hưởng và phối hợp

- API: không đổi endpoint hoặc schema. Client vẫn dùng `/garment3d/generations`, `/garment3d/jobs/{id}`, `/garment3d/generations/{id}`; origin dev mặc định là `http://localhost:8001`. M3 cần cấp origin production qua `VITE_GARMENT3D_API_URL` và vận hành service riêng.
- Đơn vị: không đổi GLB mét hay số đo API centimet. M2 cần duy trì metadata `fit_ready`, landmark và URL asset như contract hiện tại.
- Database: không đổi. SQLite job của service garment vẫn theo cấu hình hiện có.
- Asset: trang mới tiếp tục xem/tải GLB và metadata qua service garment. Backend body hiện chỉ nhận `garment_id` catalog; GLB tạo từ ảnh chưa được mặc lên body. Đây là ranh giới đã xác nhận khi chọn phạm vi tích hợp trang và menu.
- Xung đột Git: không có conflict trong đợt sửa này. Rủi ro còn lại: nếu production thiếu `VITE_GARMENT3D_API_URL` hoặc service garment chưa chạy, thao tác tạo mô hình sẽ lỗi; tài liệu chạy đã nêu cấu hình cần thiết.

## Kiểm tra và bàn giao

- `npm.cmd run build`: pass; `dist/index.html` cùng chunk lazy `Garment3DPage` được tạo. Vite cảnh báo chunk chính lớn hơn 500 kB; không làm build thất bại.
- `git diff --check`: pass.
- Trình duyệt Playwright trên Vite dev: menu desktop mở `/garment-3d`, URL cũ `/garment3d.html` chuyển tiếp đúng, mobile 375 px có menu và không tràn ngang, nút Back trở lại `/`.
- Trình duyệt Playwright với API mô phỏng: upload từ trang tích hợp gọi POST generation, GET job, GET generation tại cổng 8001 và hiện link tải GLB. Đây là kiểm tra UI/API contract bằng phản hồi mô phỏng, chưa phải kiểm thử service thật qua trình duyệt.
- Kiểm thử người dùng đã cung cấp ở lượt trước: 20 test garment/backend pass sau khi cài phụ thuộc; các test đó không được chạy lại trong đợt sửa frontend này.
- Bàn giao: M5 kiểm tra thêm upload ảnh thật trên trang tích hợp với service 8001; M3 cấu hình origin production. Việc mặc GLB do service tạo lên body cần một contract và luồng xử lý riêng nếu được yêu cầu sau.
