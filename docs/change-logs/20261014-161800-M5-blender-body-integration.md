# Tích hợp body Blender vào giao diện thử đồ

## Vai trò và mục đích

- Thời điểm: 2026-10-14 16:18 Asia/Saigon.
- Vai trò điều phối đợt sửa: M5 (giao diện); mã liên quan M1 (tạo body), M3 (API/job/asset). M2 là owner của asset trang phục tùy chọn.
- Mục đích: đưa khả năng tạo body GLB từ thông số, xem mô hình và mặc trang phục từ `body/BlenderTest` vào kiến trúc và giao diện hiện có, không chạy server/giao diện độc lập của source tham chiếu.

## File thay đổi (trước → sau)

| File | Trước → sau; hàm/trường liên quan |
| --- | --- |
| `body/estimation/blender_body.py` | Chưa tồn tại → script Blender riêng: `mpfb_body`, `mannequin`, `make_body`, `make_clothing`, `main`; xuất GLB Y-up từ tham số đã kiểm tra ở API. |
| `backend/services/blender_body.py` | Chưa tồn tại → `BlenderBodyJobs` quản lý job Blender trong bộ nhớ, chạy subprocess có timeout, giới hạn hai job, lưu GLB theo UUID trong `data/outputs/blender_body/`. |
| `backend/api/body_builder.py` | Chưa tồn tại → model `BodyParameters`, `ClothingParameters` và route generate, clothing, jobs, assets dưới `/api/body-builder`. |
| `backend/main.py` | Trước chỉ đăng ký API mock/fit/asset → đăng ký thêm router `body_builder`. |
| `frontend/src/api/bodyBuilderApi.ts` | Chưa tồn tại → kiểu tham số/job, POST và poll job Blender, ghép URL asset bằng `VITE_API_URL`. |
| `frontend/src/components/tryon/BodyBuilderStep.tsx` | Chưa tồn tại → form chiều cao/cân nặng/tuổi/giới tính/màu da, 9 tỷ lệ và preset bằng style dự án. |
| `frontend/src/components/tryon/GeneratedBodyViewer.tsx` | Chưa tồn tại → tải GLB Blender, body/trang phục, xoay/zoom, khung lưới, đổi màu, tải GLB; giải phóng WebGL khi rời trang. |
| `frontend/src/pages/tryon/TryOnPage.tsx` | Trước chỉ có luồng ảnh/mock → thêm nhánh body Blender, gọi generate/clothing theo bước hiện có, hiển thị lỗi và tái dùng body job khi đổi trang phục/size. |
| `frontend/src/components/tryon/UploadStep.tsx` | Trước chỉ có đường ảnh và tuyên bố phân tích thật → thêm nút vào body builder, đổi mô tả ảnh thành luồng dữ liệu mẫu. |
| `frontend/src/components/tryon/SelectGarmentStep.tsx` | Trước chỉ xem 4 sản phẩm, size cố định và nhãn fit tự suy → dùng size sẵn có của sản phẩm, hiển thị tất cả sản phẩm, bỏ khuyến nghị/fit chưa có căn cứ. |
| `frontend/src/components/tryon/ProcessingStep.tsx` | Trước có phần trăm, SMPL-X và độ chính xác giả → chỉ báo chờ không xác định phần trăm, mô tả trạng thái thực tế. |
| `frontend/src/components/tryon/InteractiveViewer3DStep.tsx` | Trước tự điền điểm 95, 99,4%, số đo vùng và gợi ý AI → hiển thị null là chưa có và gắn nhãn mock. |
| `frontend/src/api/tryonApi.ts` | Trước fallback client tự tạo điểm fit → điểm vùng/tổng null, dùng API base từ config và mô tả tiến trình demo. |
| `frontend/src/styles/tryon.css` | Trước thiếu style body builder → thêm form, viewer, trạng thái lỗi và hoạt ảnh chờ trong palette hiện có. |
| `README.md` | Trước chỉ hướng dẫn API mock → thêm cách cấu hình Blender, luồng UI, API job, vị trí asset và giới hạn mô phỏng. |

## Ảnh hưởng hợp đồng và module

- API: thêm nhánh `/api/body-builder/*`, không thay schema hoặc response của `/api/tryon/analyze`, `/fit`, `/jobs` cũ. Job mới có `pending/running/completed/failed`, `method`, `source`, `asset_url`, `error`; lỗi dùng envelope chung. Frontend đã có consumer tương ứng.
- Schema: request body nhập `height_cm` 140–210, `weight_kg` 35–150, `age` 10–80, tỷ lệ 0–1; request áo dùng `body_job_id`, `garment_id`, `category`, `color_hex`, `size`. Không sinh `BodySchema` hay số đo ảnh từ thông số thủ công.
- Đơn vị/hệ trục: API chiều cao cm, script đổi sang mét; Blender làm việc Z-up và xuất GLB Y-up. Các thanh tỷ lệ không phải chu vi cm. Cần kiểm chứng trực quan GLB trên Blender cài tại máy người dùng.
- Database: không đổi; job trong RAM, restart mất ID. GLB trong `data/outputs/blender_body/` đã nằm dưới `.gitignore`.
- Asset: đọc tùy chọn `data/external/clothing/<garment_id>.glb/.obj` đã được Git bỏ qua; thiếu asset thì tạo trang phục hình khối. Asset áo cần căn chỉnh cho body tham chiếu 1,7 m; chức năng hiện không fit/drape asset vào body.
- M1: script tạo body từ tham số/MPFB2 tùy chọn, fallback mannequin. Không đo từ ảnh.
- M3: thêm endpoint/job/file serving riêng; vẫn cần xác nhận mô hình triển khai vì máy chạy API phải có Blender và lưu file cục bộ.
- M5: cùng giao diện các bước hiện tại; luồng body thủ công xem GLB thực, luồng ảnh còn viewer demo. Null/nguồn mock được hiển thị rõ hơn.
- M4: không thay công thức Fit. Reference M4 và API M3 hiện có hình dạng khác; luồng này không hòa giải hai contract đó.

## Xung đột và nguy cơ

- Đã xác nhận: backend fit mock chỉ có catalog `demo-tshirt`, frontend có nhiều sản phẩm. Luồng body Blender dùng `garment_id` từ catalog frontend và route riêng; luồng ảnh với sản phẩm khác vẫn có thể rơi vào fallback mock client. Cần M3/M5 thống nhất catalog khi tích hợp fit thật.
- Nguy cơ: MPFB2 API thay đổi giữa phiên bản; script chuyển sang mannequin nếu MPFB không dùng được và job trả `method/source` để UI gắn nhãn. Chưa có bằng chứng chạy trên Blender/MPFB của máy người dùng.
- Nguy cơ: asset trang phục tùy chọn chưa được chuẩn hóa rig/size/định vị; M2 cần bàn giao GLB/OBJ căn chỉnh trước khi coi là try-on thật.
- Nguy cơ: job/file cục bộ không phù hợp nhiều worker hoặc máy chủ không lưu trữ bền; M3 cần thiết kế queue/storage nếu triển khai nhiều instance.

## Kiểm thử và bàn giao

- Build frontend, Python test, Blender headless và kiểm tra UI trình duyệt: **chưa chạy**. Không có log test do user cung cấp; Rule 01 của repo yêu cầu user tự chạy terminal/test. Chỉ rà soát tĩnh mã và contract.
- M5 cần nhận kết quả `npm.cmd run build` và kiểm tra các đường thành công/lỗi/timeout, đổi sản phẩm/size/màu, xem/tải GLB, cleanup viewer.
- M3/M1 cần nhận kết quả khởi động API và một job `generate`/`clothing` trên Blender thực, xác nhận kích thước/trục GLB, asset route, lỗi khi thiếu Blender và hành vi MPFB/fallback.
- M2 cần xác nhận quy ước asset áo 1,7 m nếu cung cấp GLB/OBJ thật; M4 tiếp tục tách riêng Fit/AI khỏi visual body thủ công.
