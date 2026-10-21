# Phòng phối đồ: áo và quần độc lập

## Vai trò, thời điểm và mục đích

- M5, 2026-10-21 23:18:23, Asia/Saigon (UTC+7).
- User yêu cầu thử sản phẩm bên ngoài, thay áo/quần độc lập và giữ chụp ảnh tạo model.
- Không chạy Git, không thay nhánh. `.git/HEAD` vẫn là `feature/body`; phạm vi frontend được User yêu cầu trực tiếp.

## File thêm/sửa và trước → sau

| File | Loại | Thay đổi |
| --- | --- | --- |
| `frontend/src/App.tsx` | Sửa | `/try-on` dùng ImageTryOnPage một món → OutfitTryOnPage phối bộ; `handleSelectProductForTryOn` nhận và giữ size từ modal |
| `frontend/src/pages/tryon/OutfitTryOnPage.tsx` | Thêm | Chưa có → slots top/bottom/dress độc lập, chọn catalog/ảnh ngoài, `apply` gọi API từng món thay đổi, lưu asset/job ảnh theo phiên, khôi phục model và theo dõi lại job |
| `frontend/src/components/tryon/BodyPhotoCapture.tsx` | Thêm | Chưa có → camera, snapshot, ảnh thiết bị, cleanup stream/URL, thông báo rõ ảnh chưa tái dựng body |
| `frontend/src/components/tryon/OutfitViewer.tsx` | Thêm | Chưa có → body chung và garment layers, kiểm tra node, WebGL/error fallback, OrbitControls và cleanup |
| `frontend/src/styles/outfit.css` | Thêm | Chưa có → bố cục viewer/tủ đồ, selection summary, responsive desktop/mobile, focus/disabled state |
| `frontend/src/api/bodyBuilderApi.ts` | Sửa | Request/polling không nhận cancellation → `request`, `waitForJob`, `generate`, `clothing` nhận AbortSignal tùy chọn, giữ tương thích caller cũ |
| `frontend/src/components/GarmentImageInputs.tsx` | Sửa | ID input cố định theo view → useId ở ViewSlot, tránh label trỏ nhầm input khi có nhiều instance |
| `frontend/src/data/sizeCharts.ts` | Sửa | Record yêu cầu cả auto nhưng không có bảng auto gây TS2741 → bảng chỉ có loại cụ thể; hàm trả null khi chưa xác định loại |
| `frontend/src/components/SizeChartPanel.tsx` | Sửa | Truy cập profile trực tiếp → xử lý null bằng thông báo chưa xác định loại trang phục |
| `frontend/src/pages/Garment3DPage.tsx` | Sửa | Tính scale từ profile luôn có → giữ scale 1 khi không có profile, không giả lập bảng size cho auto |
| `frontend/src/pages/tryon/ImageTryOnPage.tsx` | Sửa | Mapping loại ảnh khai báo bao gồm auto nhưng thiếu key → Exclude auto ở luồng chọn loại cụ thể |
| `frontend/tests/outfit-manual.md` | Thêm | Chưa có → 14 kịch bản TC-WEB-OUTFIT và kết quả mong đợi, trạng thái chưa chạy |
| `.agents/memory/ACTIVE_CONTEXT.md` | Sửa | Ngữ cảnh kiểm tra conflict → bổ sung yêu cầu UI, triển khai, quyền hạn, trạng thái kiểm thử và bàn giao |
| `docs/change-logs/20261021_231823_M5_outfit_fitting_room.md` | Thêm | Chưa có → nhật ký đợt thay đổi này |

## Ảnh hưởng

- **API/schema:** không sửa server hoặc wire schema. Tiếp tục `/api/body-builder/generate`, `/bodies/{id}`, `/clothing` và `/api/tryon/image-jobs`. Ảnh catalog được fetch phía browser rồi gửi như file; lỗi CORS có thông báo tải ảnh từ thiết bị. Có thể tạo hai job tuần tự cho áo/quần; không tuyên bố backend đã hỗ trợ outfit job chung.
- **Đơn vị/hệ trục:** chiều dài gửi cm; GLB giữ mét, Y-up, +Z forward. Viewer chỉ dịch cả nhóm theo body, không scale/căn giữa từng garment.
- **Database:** không sửa database hoặc migration. Job ảnh tiếp tục dùng lưu trữ server hiện có.
- **Asset:** không thêm model, ảnh hay file >50MB. Chỉ thêm mã, CSS và Markdown. GLB từng món chứa body nên viewer loại body trùng; chưa xuất GLB cả bộ.
- **Lưu trình duyệt:** body ID giữ key localStorage hiện có; lựa chọn/kết quả/job ID theo phiên ở `tryon.outfit.v1`. Không ghi ảnh cá nhân hoặc File vào storage. Ảnh chưa gửi phải chọn lại sau reload; job đã gửi có thể tiếp tục polling.
- **M1:** không sửa thuật toán/model. Ảnh người dùng chỉ xem trước, model được tạo bằng thông số. Chưa tích hợp tái dựng từ ảnh.
- **M2:** đã đọc `mesh_builder.py` xác nhận GarmentFront/Back/Seams; đọc `blender_fitting.py` xác nhận garment có thể là con human. Renderer dùng layers để không ẩn garment con. E2E asset thực tế **chưa kiểm tra**.
- **M3:** không sửa API. `body-builder` còn phụ thuộc job bộ nhớ và scene native; phục hồi sau restart **chưa kiểm tra**. Worker vẫn cần chạy cho đường ảnh.
- **M4:** không thêm hoặc suy diễn score/recommendation; chưa có đánh giá size hay tương tác vải áo–quần.

## Xung đột xác nhận và nguy cơ

- Xác nhận từ code cũ: initialGarment của ImageTryOnPage chỉ quyết định garmentType, không đưa ảnh/asset sản phẩm vào xử lý. Luồng mới phân biệt catalog asset và ảnh sản phẩm, chuyển đúng sản phẩm/size.
- Cấu trúc mesh khác quy ước có thể không tách được lớp: viewer báo lỗi rõ và giữ phần đã tải; cần owner M2/M3 xác nhận tên node, không đoán hoặc sửa ngầm.
- Body nguyên bản có thể chưa áp dụng tổng hợp occlusion mask cho nhiều MHCLO. Cần kiểm tra xuyên mesh giữa body/áo/quần với asset thật; chưa có mô phỏng liên trang phục.
- Nếu rời trang, cancellation chỉ dừng client; job Blender/server có thể tiếp tục. Job ảnh đã lưu có nút tiếp tục; job generate body không được bổ sung persistence phía server.

## Kiểm thử và bằng chứng

- **Build PASS**, chưa chạy test/browser/Blender E2E.
- Đã đối chiếu tĩnh caller, endpoint, schema ảnh, prefix mesh và quan hệ parent garment/body từ code trong repo.
- User đã trả lời “Cho phép chạy build” cho `npm.cmd run build` trong frontend.
- Build đầu FAIL: TS2741 tại sizeCharts.ts (2 mapping) và ImageTryOnPage.tsx (2 mapping) vì GarmentType có auto; đã sửa khai báo và null state ở consumer.
- Build lại PASS, exit 0: TypeScript + Vite 5.4.21, 669 modules transformed, built in 14.03s. Main JS 998.45 kB/gzip 272.36 kB; Vite cảnh báo chunk >500 kB, không chặn build. Sinh artifact trong frontend/dist theo script build; không commit.
- Kịch bản bàn giao: `frontend/tests/outfit-manual.md`, TC-WEB-OUTFIT-01 đến TC-WEB-OUTFIT-14.

## Bàn giao

- User/M5: build đã qua; tiếp tục kiểm tra UI desktop/mobile và camera cho phép/từ chối.
- M2/M3: chạy E2E hai món, đổi từng món, catalog refit/reference assets, lỗi worker/GLB, restart backend và xuyên mesh. Xác nhận adapter tên node trước khi thay pipeline xuất GLB.
- M1: nếu cần model suy từ ảnh thật, cần contract/pipeline riêng; UI hiện ghi đúng khả năng từ thông số.
