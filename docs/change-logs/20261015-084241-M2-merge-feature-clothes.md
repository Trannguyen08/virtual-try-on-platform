# Merge feature/clothes into feature/backend-tryon-flow

- Thời điểm: 2026-10-15 08:42 Asia/Saigon.
- Vai trò: M2 (garment), phối hợp M3 (API) và M5 (frontend).
- Mục đích: nhập commit `11e7e3f` từ `feature/clothes`, giải quyết conflict và giữ các luồng hiện có.

## File và thay đổi trước → sau

Các file sau chưa có trên nhánh đích trước merge; sau merge có nội dung từ nhánh nguồn:

| File thêm | Nội dung sau merge |
| --- | --- |
| `AGENTS.md` | Chỉ dẫn agent do nhánh nguồn mang vào. |
| `backend/garment3d/.env.example` | Mẫu cấu hình service trang phục. |
| `backend/garment3d/README.md` | Cách chạy và contract API trang phục. |
| `backend/garment3d/__init__.py` | Package Python của service. |
| `backend/garment3d/app.py` | FastAPI entrypoint riêng và lifespan khởi tạo provider. |
| `backend/garment3d/models.py` | Trạng thái job và bản ghi lưu trữ. |
| `backend/garment3d/repository.py` | Lưu job bằng SQLite. |
| `backend/garment3d/requirements-dev.txt` | Phụ thuộc phát triển và test của service. |
| `backend/garment3d/requirements.txt` | Phụ thuộc runtime, gồm OpenCV. |
| `backend/garment3d/router.py` | Route `/garment3d/generations`, jobs và artifacts. |
| `backend/garment3d/schemas.py` | Response schema cho generation/job/assets. |
| `backend/garment3d/service.py` | Điều phối xử lý và cập nhật trạng thái job. |
| `backend/garment3d/settings.py` | Đọc và kiểm tra cấu hình service. |
| `backend/garment3d/uploads.py` | Kiểm tra và lưu ảnh tải lên. |
| `frontend/GARMENT3D.md` | Cách chạy trang mới; sau khi merge mô tả hai backend và build hai trang. |
| `frontend/garment3d.html` | HTML entrypoint cho trang Garment 3D. |
| `frontend/src/api/garment3d.ts` | Client API; sau khi merge hỗ trợ `VITE_GARMENT3D_API_URL` riêng. |
| `frontend/src/components/GarmentGenerationProgress.tsx` | Tiến độ tạo model. |
| `frontend/src/components/GarmentImageInputs.tsx` | Nhập ảnh các góc của áo. |
| `frontend/src/components/SizeChartPanel.tsx` | Hiển thị bảng size. |
| `frontend/src/data/sizeCharts.ts` | Dữ liệu bảng size cho giao diện. |
| `frontend/src/garment3d-main.tsx` | React entrypoint của trang mới. |
| `frontend/src/hooks/useGarmentGeneration.ts` | Polling trạng thái generation. |
| `frontend/src/pages/Garment3DPage.tsx` | Trang tạo và xem trang phục 3D. |
| `frontend/src/styles/garment3d.css` | Kiểu hiển thị trang mới. |
| `frontend/src/viewer/Garment360Viewer.tsx` | Viewer GLB. |
| `frontend/src/viewer/garmentAnnotations.ts` | Chú thích số đo trên viewer. |
| `frontend/vite.garment3d.config.ts` | Cấu hình build; sau khi merge xuất cả `index.html` và `garment3d.html`. |
| `garment/reconstruction/__init__.py` | Package reconstruction. |
| `garment/reconstruction/config.py` | Preset pipeline. |
| `garment/reconstruction/contracts.py` | Hợp đồng garment metadata và enum. |
| `garment/reconstruction/errors.py` | Lỗi miền reconstruction. |
| `garment/reconstruction/local_pipeline.py` | Tạo mesh/texture từ ảnh local. |
| `garment/reconstruction/postprocessing.py` | Xử lý sau bằng Blender hoặc passthrough. |
| `garment/reconstruction/preprocessing.py` | Kiểm tra và chuẩn bị ảnh. |
| `garment/reconstruction/providers/__init__.py` | Export provider. |
| `garment/reconstruction/providers/local.py` | Provider local. |
| `garment/reconstruction/providers/mock.py` | Provider mock cho test. |
| `garment/reconstruction/providers/tripo.py` | Provider Tripo tùy chọn. |
| `garment/reconstruction/validation.py` | Kiểm tra GLB đầu ra. |
| `scripts/blender/process_garment.py` | Script xử lý garment trong Blender. |
| `tests/integration/garment_3d/test_local_api.py` | Test API với pipeline local. |
| `tests/integration/garment_3d/test_mock_api.py` | Test API với provider mock. |
| `tests/unit/backend/garment3d/test_repository.py` | Test lưu job. |
| `tests/unit/garment/reconstruction/test_local_pipeline.py` | Test pipeline local. |
| `tests/unit/garment/reconstruction/test_postprocessing.py` | Test hậu xử lý. |
| `tests/unit/garment/reconstruction/test_preprocessing.py` | Test tiền xử lý. |
| `tests/unit/garment/reconstruction/test_tripo_provider.py` | Test provider Tripo. |
| `tests/unit/garment/reconstruction/test_validation.py` | Test validate asset. |

File đã có trước merge:

| File | Trước → sau |
| --- | --- |
| `.gitignore` | Chưa ignore dataset/cache M4 → thêm `ai/dataset/data/`, `tmp/hf_cache/`, `.ipynb_checkpoints/`; giữ các rule ignore của nhánh đích. |
| `frontend/package.json` | Build một trang → gọi cấu hình Vite xuất cả hai trang. |
| `frontend/tsconfig.json` | Target ES2020 → ES2021 và thêm các tùy chọn TypeScript từ nhánh nguồn; giữ các tùy chọn hiện có. |

`backend/main.py` và `pytest.ini` có conflict nhưng kết quả giữ nội dung nhánh đích, nên không đổi nội dung sau merge. Không có file bị xóa trong kết quả merge.

## Ảnh hưởng và phối hợp

- API: thêm service riêng với prefix `/garment3d`; API hiện có dưới `/api` và entrypoint `backend.main:app` giữ nguyên. M3 cần quản lý cách chạy/deploy service mới.
- Schema và đơn vị: metadata garment từ nhánh nguồn dùng cm ở API, m trong GLB, Y-up và +Z forward; chưa kiểm chứng bằng pipeline local trong môi trường này. M1/M4 cần đối chiếu khi nối với body và Fit.
- Database: service mới ghi SQLite theo `Garment3DSettings.sqlite_path`; không thay đổi database của backend hiện có. M3 quản lý lưu trữ và vòng đời job.
- Asset: thêm GLB, thumbnail và metadata URL của service mới. M5 dùng `VITE_GARMENT3D_API_URL` khi chạy đồng thời hai backend; trang chính và trang garment được build cùng lúc.
- Xung đột đã xác nhận: 4 conflict Git ở `.gitignore`, `backend/main.py`, `frontend/tsconfig.json`, `pytest.ini`; đã giải quyết. Nguy cơ còn lại: pipeline local thiếu `cv2` trong `.venv` hiện tại, cần cài bộ phụ thuộc của service rồi chạy test local.

## Kiểm tra và bàn giao

- `python -m pytest tests/unit/backend tests/integration/garment_3d/test_mock_api.py -q --tb=short` bằng `.venv`: 53 passed.
- `npm.cmd run build` tại `frontend`: pass, có cả `dist/index.html` và `dist/garment3d.html`.
- `git diff --cached --check`: pass.
- `tests/unit/garment/reconstruction` và `test_local_api.py`: chưa chạy thành công vì thiếu `cv2` khi import; không coi là test pass.
- Còn lại: cài phụ thuộc trong `backend/garment3d/requirements-dev.txt` ở môi trường phù hợp, chạy test pipeline local và cấu hình service khi deploy. Không thay đổi công thức Fit M4.
