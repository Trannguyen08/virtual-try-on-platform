---
name: m5-frontend-expert
description: Hướng dẫn agent M5 triển khai giao diện thử đồ, API, polling và viewer 3D với trạng thái mock/real minh bạch.
---

# M5 FRONTEND EXPERT

## Điều kiện kích hoạt

Dùng khi nhiệm vụ giao M5 hoặc liên quan frontend/src/, frontend/tests/, trải nghiệm upload, gọi API, polling, GLB viewer và kết quả Fit. Đọc Rule 01–02, Rule 09 và Rule 10 trước khi sửa.

## Hiện trạng đã đối chiếu

Nhánh feature/backend-tryon-flow có TryOnPage theo bước upload/chọn áo/processing/viewer, frontend/src/api/tryonApi.ts gọi analyze/fit/jobs và fallback mock phía client, InteractiveViewer3DStep.tsx dựng avatar/quần áo hình học bằng Three.js. Có nhiều component giao diện; useTryOn.ts, useJobPolling.ts, ModelLoader.ts, Heatmap.ts, Scene.tsx, FitPanel.tsx và ResultPage.tsx được xem còn placeholder. Viewer đang dựng hình minh họa, không phải tải và drape GLB thật. Fallback client hiện tạo score demo, trong khi contract mock M3 trả score null; đây là khác biệt cần M3–M5 thống nhất, không xem score demo là điểm Fit thật.

## Input và output

- Input API M3: response envelope data/error, Body với measurements *_cm và mesh, catalog, Job với status/result/error, FitResult với recommendation/overall/regions/assets và provenance.
- Output M5: trạng thái UI, polling, thông báo lỗi, hiển thị số đo/fit và viewer. Hiển thị rõ source=mock/mixed, null là “chưa có”, không trình bày số synthetic như đo thật.
- Asset URL tương đối phải ghép với backend origin. GLB m, Y-up, +Z forward; chọn tryon_mesh hoặc body_mesh cộng garment_mesh. Không suy diễn heatmap khi API chưa có.

## Quy trình làm việc

1. Đọc docs/api/api-contract.md, backend/schemas/** liên quan và frontend/src/api/tryonApi.ts trước khi đổi kiểu dữ liệu hay UI.
2. Tách rõ dữ liệu API, fixture và fallback client; mô tả đúng trạng thái từng đường đi. Trình thiết kế và xin duyệt theo Rule 01.
3. Xử lý input upload, validation phía UI, 202 job, polling terminal state, timeout, failed và API error; không nuốt lỗi thành kết quả thật. Phối hợp M3 nếu behavior API cần đổi.
4. Xây viewer theo asset do M3 phát, giữ hệ trục M1/M2 và dọn tài nguyên Three.js khi component rời trang. Dữ liệu M4 chỉ được hiển thị theo contract tích hợp đã chốt.
5. Kiểm tra nội dung UI tránh khẳng định AI/SMPL-X/mô phỏng vải đã chạy khi source vẫn mock. Gọi change-impact-log sau đợt sửa.

## Kiểm thử và bàn giao

Đề xuất user chạy build/test frontend theo Rule 01, kiểm tra upload hợp lệ/lỗi, polling completed/failed/timeout, null/source và viewer khi asset thiếu. Kiểm tra e2e với API M3 khi có môi trường; test HTTP backend không thay thế test browser. Nếu chưa có log chạy, ghi chưa chạy. Bàn giao component, trường API cần M3 xác nhận, giới hạn mock/asset/heatmap và ảnh bằng chứng UI.

## Tài liệu kỹ thuật

Tham khảo [threejs-viewer-setup.md](references/threejs-viewer-setup.md), [heatmap-colormap.md](references/heatmap-colormap.md) và [ux-flows-and-states.md](references/ux-flows-and-states.md) khi thiết kế M5; đối chiếu với API và viewer đang chạy trước khi áp dụng.
