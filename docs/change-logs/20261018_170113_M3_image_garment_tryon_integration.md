# Change Impact Log — luồng thử đồ từ ảnh trang phục

- Thời điểm: 2026-10-18 17:01:13 Asia/Saigon.
- Vai trò thực hiện: M3 tích hợp; phạm vi được người dùng duyệt gồm M3, M2 và M5. Owner chịu ảnh hưởng: M1 cho asset MPFB, M2 cho mesh trang phục và Blender, M3 cho API/job/storage, M5 cho trang thử đồ.
- Mục đích: dùng body MPFB đã tạo và ảnh trang phục người dùng tải lên để tạo một GLB thử đồ tĩnh có job bền vững, lỗi rõ ràng và viewer riêng.

## File đã thay đổi (trước → sau)

| File | Trước → sau, điểm mã liên quan |
| --- | --- |
| `.gitignore` | Chưa loại kho người dùng → bỏ qua `data/assets/` để ảnh và GLB không vào Git. |
| `backend/db/models.py` | Chưa có job ảnh → thêm `ImageTryOnRecord` với trạng thái, request/result/error JSON, lease và số lần thử. |
| `backend/db/migrations/versions/20261018_0002_image_tryon_queue.py` | Chưa tồn tại → migration bảng `image_tryon_jobs`, FK body, index trạng thái/thời gian và constraint. |
| `backend/db/repository.py` | Chỉ có body/asset/job mock → thêm `ImageTryOnRepository.enqueue/get/claim/finish`, lưu asset ảnh và job cùng giao dịch, claim có lease. |
| `backend/schemas/image_tryon.py` | Chưa tồn tại → hợp đồng `ImageTryOnRequest/Job/Result`, giới hạn loại áo/chiều dài, trạng thái và provenance. |
| `backend/services/storage.py` | Chưa có cách lấy body MPFB đã quản lý → thêm `mpfb_body_path` kiểm tra row và asset. |
| `backend/services/blender_body.py` | Body job chỉ ở RAM và GLB trong `data/outputs` → `BlenderBodyJobs(storage)` đăng ký GLB body đã xác thực vào kho quản lý và trả `body_id`. Job đang chạy vẫn ở RAM. |
| `backend/api/body_builder.py` | Dùng singleton job RAM → dùng `app.state.body_jobs`; thêm `GET /api/body-builder/bodies/{body_id}` để tra body hoàn tất sau restart. |
| `backend/services/image_tryon.py` | Chưa tồn tại → kiểm tra body, MIME/bytes/pixel ảnh, lưu ảnh gốc an toàn rồi enqueue; dọn file khi giao dịch thất bại. |
| `backend/api/image_tryon.py` | Chưa tồn tại → POST multipart và GET polling `/api/tryon/image-jobs`. |
| `backend/core/config.py` | Chưa có giới hạn riêng ảnh áo → thêm 10 MiB và 16 triệu pixel mỗi ảnh. |
| `backend/main.py` | Chưa khởi tạo dịch vụ try-on ảnh → nối storage/body jobs/image try-on router vào app. |
| `garment/simulation/blender/compose_tryon.py` | Chưa tồn tại → import hai GLB, kiểm tra frame và tỉ lệ, đặt áo theo chiều cao body, chỉnh khoảng hở bề mặt, kiểm tra xuyên mesh, export GLB và báo cáo; từ chối simulation chưa hiệu chuẩn. |
| `backend/workers/__init__.py` | Chưa tồn tại → đánh dấu package worker. |
| `backend/workers/image_tryon.py` | Chưa tồn tại → worker claim PostgreSQL, xác thực hash ảnh, gọi pipeline local M2, kiểm tra GLB/vật liệu, gọi Blender, đăng ký GLB cuối, ghi kết quả/lỗi; kết quả có dấu vết reconstruction. |
| `frontend/src/api/bodyBuilderApi.ts` | Chỉ dùng job body RAM → hỗ trợ `body_id`, endpoint khôi phục body và ghép URL asset với backend origin. |
| `frontend/src/api/imageTryOnApi.ts` | Chưa tồn tại → client multipart, polling, kiểu kết quả, URL GLB; không có fallback mock. |
| `frontend/src/components/GarmentImageInputs.tsx` | Bộ chọn ảnh nhận BMP cho garment3d → `tryOnImagesOnly` giới hạn JPEG/PNG/WebP và nêu giới hạn upload ở luồng mới. |
| `frontend/src/components/tryon/BodyBuilderStep.tsx` | Nút không có trạng thái chờ → `disabled` khi đang tạo body, nhãn nút nói rõ thao tác MPFB. |
| `frontend/src/pages/tryon/ImageTryOnPage.tsx` | Chưa tồn tại → tạo/chọn body, upload 1–4 ảnh áo, nhập chiều dài thật, tạo/poll job, tải đúng GLB tổng hợp. |
| `frontend/src/App.tsx` | `/try-on` trỏ trang ghép quần áo minh họa → trỏ `ImageTryOnPage`. Trang cũ vẫn còn trong mã. |
| `tests/unit/backend/test_image_tryon.py` | Chưa tồn tại → TC-API-09/02/03 cho enqueue, restart, đầu vào sai, lease và lỗi worker. Fixture GLB chỉ phục vụ test contract. |
| `tests/unit/backend/test_persistence.py` | Kiểm tra bốn bảng cũ → thêm xác nhận bảng job ảnh thứ năm trong migration và sửa docstring. |
| `docs/api/api-contract.md` | Chỉ mô tả mock/garment3d riêng → thêm contract v0.2, trạng thái, trường reconstruction, đơn vị và giới hạn. |
| `docs/development/body-garment-tryon-integration-plan.md` | Kế hoạch chưa nối vào mã → ghi trạng thái triển khai v0.2 và những phần chưa nghiệm thu. |
| `docs/testing/test-cases/test-cases-backend-persistence.md` | TC-API-08 nêu bốn bảng cũ → cập nhật kỳ vọng năm bảng sau migration mới và thêm TC-API-09, đánh dấu chưa chạy. |
| `docs/development/image-tryon-runbook.md` | Chưa tồn tại → hướng dẫn người vận hành migration/API/worker/frontend, thử thủ công và giới hạn hiện tại. |

## Ảnh hưởng hợp đồng và dữ liệu

- API: thêm POST/GET `/api/tryon/image-jobs` và GET body hoàn tất; `/api/tryon/fit` mock vẫn là hợp đồng riêng. UI `/try-on` chuyển sang job ảnh thực; người dùng phải nhập `garment_type` và chiều dài thật.
- Schema: request dùng `body_id`, `reference_measurement=garment_length`, `reference_value_cm`; response có provenance, `simulation_ran`, `penetration_fraction`, `reconstruction` và URL GLB. Ảnh nguồn không có URL công khai.
- Đơn vị/hệ trục: số đo ngoại vi cm; nội bộ mesh m, Y-up, +Z forward. Metadata body và garment được kiểm tra trước ghép; Blender import chuyển sang frame nội bộ của Blender khi xử lý.
- Database: thêm bảng queue qua migration 0002. Ảnh được ghi trước transaction metadata; khi enqueue lỗi, thư mục ảnh được dọn. Worker cần cùng database và thư mục asset với API.
- Asset: body GLB MPFB và GLB tổng hợp được đăng ký ở `data/assets/` và phục vụ qua `/api/assets`; worker kiểm tra SHA của ảnh nguồn và tránh ghi đè asset đã đăng ký khi retry.
- Liên module: M1 cần xác nhận MPFB export đúng tư thế và frame đã khai báo; M2 cần xác nhận hình học/texture sau Blender; M5 cần kiểm tra viewer thật. M4 chưa có fit score, size hoặc AI fit trong luồng này.

## Xung đột, nguy cơ và việc cần phối hợp

- Xung đột đã xác nhận: trang `/try-on` cũ dùng đồ minh họa; route nay dùng ảnh do người dùng tải lên. Trang cũ vẫn ở mã nhưng không còn là route đang dùng.
- Nguy cơ chưa nghiệm thu: mốc đặt áo theo tỉ lệ chiều cao và BVH clearance có thể sai với một số áo/quần; cần ảnh thật và body MPFB thật để kiểm tra, điều chỉnh thuật toán. Không có rig động hay cloth solver; `simulate_cloth=true` trả lỗi có cấu trúc.
- Nguy cơ vận hành: job queue PostgreSQL cần worker riêng; `data/assets/` phải bền vững và chia sẻ. Body job đang tạo vẫn ở RAM, nên API restart khi đang tạo body sẽ mất trạng thái job đó. Kết quả body đã hoàn tất được tra lại từ database.
- Phạm vi chưa đáp ứng toàn bộ kế hoạch: loại áo do người dùng chọn, chưa có bộ phân loại tự động; pipeline local parametric suy phần không quan sát từ ảnh, không dùng provider Tripo hoặc đánh giá fit của M4.

## Kiểm thử và bàn giao

- Test, build, migration, Blender E2E: **chưa chạy** trong đợt này theo Rule 01 và quyền người dùng chỉ cho phép PowerShell đọc file. Không có log thực thi để tuyên bố pass.
- Đã rà tĩnh các route, schema, repository, worker, pipeline local, body export, frontend client/viewer và tài liệu; đây không thay cho nghiệm thu.
- Người vận hành chạy các lệnh trong `docs/development/image-tryon-runbook.md`, kiểm tra TC-API-09 trên PostgreSQL thật và thực hiện các ô nghiệm thu còn trống trong kế hoạch. Nếu phát hiện lỗi Blender/mesh, phối hợp M1/M2/M3/M5 theo owner ở trên.
