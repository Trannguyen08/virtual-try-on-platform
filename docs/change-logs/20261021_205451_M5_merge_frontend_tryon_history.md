# Change Impact Log — merge feature/frontend-tryon-history

- Thời gian: 2026-10-21 20:54:51 Asia/Saigon
- Vai trò thực hiện: M5; owner liên quan: M2 (Blender placement), M3 (worker, cấu hình DB và API), M5 (giao diện).
- Mục đích: tích hợp `origin/feature/frontend-tryon-history` vào `integration/tryon-body-garment-fit`; bảo vệ output trong `data/assets/` và giữ lịch sử đã xóa hết ở trạng thái rỗng.

## File thay đổi (trước → sau)

- `.gitignore`: chưa ignore `data/assets/` trong HEAD → dùng dòng ignore đã có sẵn trong working tree trước merge và đưa vào merge commit.
- `.agents/rules/project_rules.md`, `PROJECT_RULES.md`: chưa tồn tại → tài liệu quy tắc và hướng dẫn từ nhánh nguồn; nội dung cần owner đối chiếu với `AGENTS.md` trước khi áp dụng.
- `Makefile`: lệnh `dev-backend` chưa loại `.venv` khỏi reload → thêm `--reload-exclude ".venv"`.
- `backend/core/config.py`: mặc định SQLite, chưa đọc `.env` tại đây → đọc `.env` và mặc định PostgreSQL; `.env` hiện có `DATABASE_URL` nhưng không ghi giá trị vào log.
- `backend/workers/image_tryon.py`: chỉ quét lỗi Blender ở một nhánh exit code → luôn quét mã lỗi sau khi chạy và cập nhật thông điệp lỗi.
- `docs/api/api-contract.md`: `reference_value_cm` mô tả là chiều dài thật → mô tả mốc chiều dài do UI có thể ước lượng.
- `docs/change-logs/20261021_151236_M3_switch_tryon_db_to_postgres.md`, `docs/change-logs/20261021_153229_M2_mesh_guard_and_tryon_ui.md`: chưa có → ghi nhận thay đổi nguồn.
- `frontend/public/models/body_athletic.glb`, `body_curvy.glb`, `body_default.glb`, `body_female_mpfb.glb`: chưa có → thêm asset mẫu tĩnh, từng file dưới 50 MB.
- `frontend/src/App.tsx`: lịch sử placeholder → nối `HistoryPage`, modal chi tiết sản phẩm và điều hướng; bỏ khoảng trắng thừa trong vùng sửa.
- `frontend/src/components/catalog/ProductDetailModal.tsx`: chưa có → modal chi tiết sản phẩm.
- `frontend/src/components/history/CompareModal.tsx`, `HistoryCard.tsx`, `HistoryStatsBar.tsx`, `HistoryToolbar.tsx`: chưa có → thành phần trang lịch sử và so sánh.
- `frontend/src/components/home/FeaturedProductsSection.tsx`, `frontend/src/pages/home/HomePage.tsx`, `frontend/src/pages/catalog/CatalogPage.tsx`: liên kết sản phẩm trực tiếp sang thử đồ → thêm đường mở modal chi tiết; catalog tiếp tục dùng `useGarmentProducts` của integration.
- `frontend/src/components/tryon/BodyBuilderStep.tsx`, `BodyMorphingPanel.tsx`, `ConfirmTryOnStep.tsx`, `InteractiveViewer3DStep.tsx`, `frontend/src/data/bodyPresets.ts`: giao diện body/viewer cũ → thêm preset, morphing, bước xác nhận và lưu lịch sử.
- `frontend/src/data/mockHistory.ts`, `frontend/src/pages/history/HistoryPage.tsx`, `frontend/src/services/historyStorage.ts`: chưa có → dữ liệu lịch sử minh họa và lưu `localStorage`; chỉnh `getHistory` để mảng rỗng đã lưu không bị thay bằng dữ liệu minh họa.
- `frontend/src/pages/tryon/ImageTryOnPage.tsx`, `frontend/src/viewer/Garment360Viewer.tsx`: luồng ảnh và viewer cũ → cập nhật UI, lỗi thân thiện và hiển thị theo nhánh nguồn.
- `frontend/src/styles/history.css`, `frontend/src/styles/productDetail.css`: chưa có → giao diện trang lịch sử và modal.
- `garment/simulation/blender/compose_tryon.py`: kiểm tra mesh với ngưỡng cũ → ngưỡng theo reconstruction mode và nới kiểm tra penetration.
- `.agents/memory/ACTIVE_CONTEXT.md`: bối cảnh trước merge → bổ sung trạng thái merge này.
- `docs/change-logs/20261021_205451_M5_merge_frontend_tryon_history.md`: chưa có → log này.

## Ảnh hưởng và xung đột

- Git merge tự động thành công, không có conflict nội dung. `docs/api/api-contract.md` và `frontend/src/pages/catalog/CatalogPage.tsx` được Git auto-merge; đã đối chiếu catalog vẫn gọi `useGarmentProducts`.
- M3: mặc định DB đổi sang PostgreSQL, cần server PostgreSQL và driver `psycopg` đã khai báo ở `backend/requirements.txt`. API `reference_value_cm` đổi cách diễn giải tài liệu, không đổi tên trường/schema. Chưa kiểm tra runtime DB/API.
- M2: ngưỡng chấp nhận mesh thay đổi trong Blender; chưa kiểm tra ảnh hưởng đến chất lượng đặt áo hoặc an toàn hình học. Đơn vị m/cm và trục Y-up, +Z forward không đổi trong đợt merge.
- M5: trang lịch sử hiện dùng dữ liệu minh họa từ `mockHistory.ts` khi chưa có dữ liệu lưu. Cần bảo đảm UI phân biệt dữ liệu minh họa với kết quả thật; chưa kiểm tra bằng trình duyệt. `App.tsx` trên HEAD trước merge vẫn trỏ `/try-on` tới `ImageTryOnPage`; ghi chú memory trước đó về `MpfbTryOnPage` không khớp trạng thái HEAD lúc bắt đầu merge.
- 12 file output từ nhánh nguồn dưới `data/assets/` đã bỏ khỏi index merge bằng `git rm --cached`; file vật lý được giữ. `.gitignore` hiện che thư mục này. Các object đó vẫn tồn tại trong lịch sử nhánh nguồn, vì merge giữ ancestry; muốn loại khỏi lịch sử Git phải xử lý riêng.
- `LichSuCommit.txt` không được theo dõi từ trước và không được đưa vào merge. `.env` không được sửa hoặc ghi nội dung ra log.

## Xác minh và bàn giao

- Git báo merge thành công, không có unmerged path; `git ls-files -- data/assets` rỗng và `git diff --cached --check` trên code/config/API không báo whitespace.
- Chưa chạy build, test, Blender hoặc thử trình duyệt theo Rule 01; chưa có kết quả PASS/FAIL runtime.
- M5 cần kiểm tra build và các luồng history, catalog, try-on; M3 cần kiểm tra kết nối DB và worker; M2 cần đánh giá mesh trên mẫu thực. Không push lên GitHub trong đợt này.
