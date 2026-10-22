# M3 Change Impact Log: tích hợp `feature/body` vào nhánh integration

- **Thời gian:** 2026-10-20 08:54:30 Asia/Saigon.
- **Vai trò:** M3, phối hợp thay đổi liên module khi merge.
- **Mục đích:** Kết hợp hai commit mới của `origin/feature/body` lên nền
  `integration/tryon-body-garment-fit`, giữ luồng lưu body MPFB/image try-on đã
  có trên nền và thêm catalog, MPFB refit, GLTF reference alignment cùng UI.
- **Nguồn:** `6d9f6e8` và `941878f`; merge-base `53e9395`.

## File đã thêm hoặc sửa

`M` = sửa; `A` = thêm. Các file `A` đã có trên nhánh nguồn và được đưa vào
integration trong merge này.

| Trạng thái | File | Thay đổi |
| --- | --- | --- |
| M | `.env.example` | Thêm cấu hình đường dẫn kho asset MPFB và garment catalog. |
| M | `backend/api/body_builder.py` | Thêm `GET /api/body-builder/garments`; giữ route dùng job manager theo app và route tra body trong storage. |
| M | `backend/garment3d/settings.py` | Đọc `.env` bằng settings cục bộ, không sửa biến môi trường tiến trình. |
| M | `backend/services/blender_body.py` | Thêm validation catalog, yêu cầu scene native cho MHCLO, kiểm tra báo cáo refit; giữ `GlbValidator`, đăng ký body vào storage và URL asset bền vững. |
| M | `body/estimation/blender_body.py` | Lưu scene MPFB native, refit trang phục, căn chỉnh GLTF tham chiếu và xuất report. |
| M | `docs/api/api-contract.md` | Giữ contract image try-on hiện có và bổ sung contract/catalog của MPFB refit. |
| A | `docs/change-logs/20261018_162248_M1_merge_backend_tryon_flow.md` | Log nguồn M1 được đưa vào từ nhánh. |
| A | `docs/change-logs/20261018_164942_M3_backend_local_startup.md` | Log nguồn M3 được đưa vào từ nhánh. |
| A | `docs/change-logs/20261019_173403_M2_synthetic_tshirt_body_builder.md` | Log nguồn M2 được đưa vào từ nhánh. |
| A | `docs/change-logs/20261019_175943_M3_blender_script_error_diagnostics.md` | Log nguồn M3 được đưa vào từ nhánh. |
| A | `docs/change-logs/20261019_180226_M2_bridge_tshirt_hem_over_leg_gap.md` | Log nguồn M2 được đưa vào từ nhánh. |
| A | `docs/change-logs/20261019_180616_M2_triangle_section_torso_sampling.md` | Log nguồn M2 được đưa vào từ nhánh. |
| A | `docs/change-logs/20261019_181033_M2_shoulder_surface_clearance.md` | Log nguồn M2 được đưa vào từ nhánh. |
| A | `docs/change-logs/20261019_183402_M2_mpfb_native_refit_milestone_a.md` | Log nguồn M2 được đưa vào từ nhánh. |
| A | `docs/change-logs/20261019_185146_M2_inspect_mens_outfit_24_zip.md` | Log nguồn M2 được đưa vào từ nhánh. |
| A | `docs/change-logs/20261019_191824_M2_dg100024_reference_alignment.md` | Log nguồn M2 được đưa vào từ nhánh. |
| A | `docs/change-logs/20261019_201723_M2_register_aotest_hoodie.md` | Log nguồn M2 được đưa vào từ nhánh. |
| A | `docs/change-logs/20261019_201940_M2_complete_aotest_asset_files.md` | Log nguồn M2 được đưa vào từ nhánh. |
| A | `docs/change-logs/20261019_203213_M2_prepare_garment_commits.md` | Log nguồn M2 được đưa vào từ nhánh. |
| A | `docs/development/cgtrader-dg100024.md` | Hướng dẫn nguồn/reference asset DG100024. |
| A | `docs/development/cgtrader-mens-outfit-24.md` | Hướng dẫn nguồn/reference asset Mens Outfit 24. |
| A | `docs/development/mpfb-refit-milestone-a.md` | Hướng dẫn cài đặt và vận hành MPFB refit. |
| A | `docs/report/evidence/garment/tshirt-template-check.md` | Ghi nhận kiểm tra template áo nguồn. |
| A | `frontend/public/images/mpfb-pants.svg` | Icon catalog quần MPFB. |
| A | `frontend/public/images/mpfb-tshirt.svg` | Icon catalog áo MPFB. |
| M | `frontend/src/api/bodyBuilderApi.ts` | Thêm kiểu garment catalog và API tải catalog; giữ URL resolver/body lookup. |
| M | `frontend/src/components/tryon/GeneratedBodyViewer.tsx` | Hiển thị provenance refit và trạng thái màu theo material gốc. |
| M | `frontend/src/components/tryon/SelectGarmentStep.tsx` | Nạp garment catalog và trạng thái availability. |
| M | `frontend/src/data/mockProducts.ts` | Bổ sung metadata chế độ fitting. |
| A | `frontend/src/hooks/useGarmentProducts.ts` | Kết hợp catalog backend với sản phẩm minh họa. |
| M | `frontend/src/pages/catalog/CatalogPage.tsx` | Hiển thị catalog garment. |
| M | `frontend/src/pages/tryon/TryOnPage.tsx` | Cập nhật thông báo tiến trình theo chế độ refit. |
| A | `garment/external/__init__.py` | Khởi tạo package chuẩn bị asset ngoài. |
| A | `garment/external/alignment.py` | Căn chỉnh garment GLTF tham chiếu theo body. |
| A | `garment/external/prepare_gltf.py` | Chuẩn hóa asset GLTF tham chiếu. |
| A | `garment/mesh/blender_tshirt.py` | Sinh mesh áo minh họa trong Blender. |
| A | `garment/mesh/torso_sections.py` | Trích tiết diện torso phục vụ dựng garment. |
| A | `garment/mesh/tshirt_geometry.py` | Hình học áo thun procedural. |
| A | `garment/mpfb/__init__.py` | Khởi tạo package MPFB. |
| A | `garment/mpfb/blender_fitting.py` | Gắn MHCLO lên topology body MPFB native. |
| A | `garment/mpfb/catalog.json` | Catalog garment và metadata nguồn/license. |
| A | `garment/mpfb/catalog.py` | Validation catalog, dependency và lựa chọn size/category. |
| A | `garment/mpfb/setup.py` | Công cụ cài asset demo có chủ đích. |
| A | `garment/mpfb/smoke.py` | Smoke helper MPFB. |
| A | `tests/unit/backend/test_blender_job_errors.py` | Ca test lỗi script Blender nguồn. |
| A | `tests/unit/backend/test_mpfb_refit_jobs.py` | Ca test job refit nguồn. |
| A | `tests/unit/garment/test_external_reference.py` | Ca test asset reference GLTF nguồn. |
| A | `tests/unit/garment/test_mpfb_catalog.py` | Ca test catalog MPFB nguồn. |
| A | `tests/unit/garment/test_mpfb_mapping.py` | Ca test mapping MHCLO nguồn. |
| A | `tests/unit/garment/test_mpfb_setup.py` | Ca test setup asset MPFB nguồn. |
| A | `tests/unit/garment/test_torso_sections.py` | Ca test tiết diện torso nguồn. |
| A | `tests/unit/garment/test_tshirt_geometry.py` | Ca test hình học áo thun nguồn. |

## Tác động và hợp đồng

- **API/schema:** Thêm `GET /api/body-builder/garments`. Các route body-builder
  hiện có tiếp tục dùng `request.app.state.body_jobs`; body GLB tiếp tục đăng ký
  qua storage. Thêm method/provenance refit và reference alignment vào kết quả
  job. `/api/tryon` mock và image try-on contract hiện có vẫn được giữ.
- **Đơn vị/trục:** Contract hiện có tiếp tục dùng GLB mét, Y-up, +Z forward.
  Asset reference phải được chuẩn hóa trước khi vào catalog.
- **Database/job:** Không có schema database migration trong thay đổi này.
  Job MPFB body-builder vẫn nằm trong RAM; storage body GLB được đăng ký như
  trước. Khôi phục job sau restart chưa được thêm.
- **Asset:** Có hai SVG nhỏ; không thấy model weight, asset garment nhị phân hoặc
  cache được thêm vào commit. Script setup tải asset vào `data/external/mpfb`;
  cần duy trì ignore/protection của thư mục dữ liệu này.
- **Module:** M1 lưu scene native; M2 cung cấp catalog, refit và chuẩn hóa
  garment; M3 validate/điều phối và đăng ký body; M5 dùng catalog và báo đúng
  provenance. M4 không đổi thuật toán hoặc contract fit.
- **Xung đột:** Đã xử lý xung đột ở `backend/api/body_builder.py`,
  `backend/garment3d/settings.py`, `backend/services/blender_body.py`,
  `docs/api/api-contract.md`, `frontend/src/api/bodyBuilderApi.ts`. Giữ phần
  storage/image-try-on của integration và ghép logic catalog/refit/settings/UI
  từ nhánh nguồn. Chưa có xung đột dữ liệu ngoài các file này được Git báo.

## Kiểm tra và bàn giao

- **Test:** Chưa chạy theo hướng dẫn phiên này. Nhánh nguồn ghi rõ không chạy
  application tests hoặc Blender validation cho commit refit; cần chạy bộ unit
  backend/garment và nghiệm thu riêng với Blender cùng asset MPFB đã cài.
- **Working tree:** Thay đổi `.gitignore` có sẵn của người dùng vẫn để ngoài
  merge; `LichSuCommit.txt` chưa track cũng được giữ nguyên.
- **Việc còn lại:** Sau merge, xác nhận `MPFB_ASSET_ROOT` có asset đã chuẩn bị,
  rà contract với owner M1/M2/M5, chạy test và Blender acceptance, rồi mới coi
  luồng refit là đã nghiệm thu. Không có xác nhận runtime trong log này.
