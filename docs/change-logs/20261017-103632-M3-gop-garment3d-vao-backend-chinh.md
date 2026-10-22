# Gộp Garment 3D vào backend cổng 8000

- Vai trò thực hiện: M3 điều phối tích hợp backend, với phần consumer M5 và dependency M2 theo yêu cầu người dùng.
- Thời điểm: 2026-10-17 10:36 Asia/Saigon.
- Mục đích: chạy API chính và Garment 3D trong cùng tiến trình `backend.main:app`, dùng cổng 8000 thay cho service riêng cổng 8001.

## File thay đổi

| File | Trước → sau | Mục liên quan |
| --- | --- | --- |
| `backend/main.py` | Chỉ có route core `/api/...` → mount Garment 3D tại `/garment3d`, khởi động/đóng provider trong lifespan của app chính; mô tả OpenAPI phân biệt core mock và dựng garment local. | `create_app`, lifespan, `app.mount`. |
| `backend/garment3d/app.py` | App độc lập luôn dùng route prefix và CORS riêng → factory nhận `route_prefix` và `use_cors` để app chính dùng prefix rỗng và CORS chung; app độc lập vẫn giữ mặc định cũ. | `create_app`. |
| `backend/garment3d/router.py` | Router tự mang prefix `/garment3d` → prefix do app đăng ký, tránh route bị lặp khi mount. | `router`. |
| `backend/requirements.txt` | Chưa kéo dependency Garment 3D → tham chiếu `garment3d/requirements.txt` để app chính có OpenCV, Trimesh và các gói cần thiết. | Runtime dependencies. |
| `.github/workflows/ci.yml` | Cài riêng OpenCV/Trimesh → cài từ requirements chung, theo dõi requirements garment trong cache và chạy test tích hợp main API. | Job `backend-and-ai`. |
| `frontend/src/api/garment3d.ts` | Dev mặc định gọi cổng 8001 hoặc biến riêng → dùng chung `API_BASE_URL` với frontend còn lại. | `GARMENT3D_API_BASE_URL`. |
| `tests/integration/garment_3d/test_main_api.py` | Chưa tồn tại → kiểm tra app chính phục vụ health Garment 3D, POST upload, job, generation, GLB và CORS của origin frontend bằng provider mock. | `TC-GARMENT-INT-02`. |
| `docs/development/run-backend-frontend.md` | Hướng dẫn ba terminal và cổng 8001 → hai terminal, API Garment 3D trên cổng 8000. | Hướng dẫn chạy local. |
| `frontend/GARMENT3D.md` | Hướng dẫn service riêng → hướng dẫn dùng backend chính và `VITE_API_URL`. | Tài liệu frontend. |
| `backend/garment3d/README.md` | Hướng dẫn chạy app độc lập → hướng dẫn chạy cùng `backend.main:app`; app factory độc lập chỉ còn dùng cho test riêng. | Tài liệu Garment 3D. |
| `docs/api/api-contract.md` | Chưa nêu namespace Garment 3D trong app chính → ghi rõ `/garment3d/...` cùng origin nhưng giữ contract response riêng với `/api/...`. | Tài liệu contract API. |

## Ảnh hưởng và phối hợp

- API: URL path Garment 3D vẫn là `/garment3d/...`; origin local đổi từ cổng 8001 sang 8000. Contract response của Garment 3D vẫn riêng, không đổi thành envelope `data/error` của core API.
- Schema và đơn vị: không sửa schema hay công thức; GLB vẫn tính theo mét, metadata/số đo API theo centimet theo code hiện có.
- Database: Garment 3D vẫn dùng SQLite tại đường dẫn cấu hình hiện có, nay khởi tạo trong vòng đời app chính. Chưa kiểm tra triển khai nhiều worker hoặc migration.
- Asset: đường dẫn `/garment3d/artifacts/...` giữ nguyên; app chính phục vụ GLB, thumbnail và metadata qua mounted sub-app.
- Module: M2 cần xác nhận pipeline reconstruction khi chạy dưới app chính; M5 dùng chung `VITE_API_URL`; M3 quản lý lifecycle, dependency và CI. M1/M4 không có code bị sửa.
- Xung đột đã xác nhận và xử lý: router cũ đã có prefix `/garment3d`, nên mount cùng prefix sẽ tạo đường dẫn lặp; prefix nay do app factory quyết định. CORS riêng của sub-app được tắt khi mount để cấu hình CORS của backend chính là nguồn duy nhất.
- Nguy cơ còn lại: môi trường Python cũ cần cài lại `backend/requirements-dev.txt`; nếu backend chính không triển khai hoặc không chạy, frontend vẫn không thể tạo garment. Chưa kiểm tra hiệu năng và storage trong môi trường production.

## Kiểm tra và bàn giao

- Kiểm tra tĩnh: đã đọc lại các file chính và tìm tham chiếu cổng 8001 trong code/tài liệu đang dùng; không còn tham chiếu đang hoạt động ngoài lịch sử change log.
- Test/build thực tế: chưa chạy theo Rule 01; chưa có log từ CI hoặc máy người dùng sau thay đổi. Test tích hợp mới được thêm vào CI nhưng chưa có kết quả.
- Bàn giao: người dùng cài lại dependency, khởi động `backend.main:app` trên cổng 8000 và frontend, rồi mở `/garment3d/health` và thử upload. M3/M5 xem kết quả CI và browser; M2 kiểm tra kết quả GLB với ảnh trang phục thật.
