# Change Impact Log — M2/M3/M5 mesh guard và image try-on UI

**Thời gian:** 2026-10-21 15:32:29 Asia/Saigon  
**Vai trò/owner:** M2 (mesh placement), M3 (worker message/API documentation), M5 (try-on UI/viewer)  
**Mục đích:** Giảm từ chối nhầm với garment dựng parametric, hiển thị body GLB sau khi tạo và đơn giản hóa bước nhập trang phục.

## File thay đổi (trước → sau)

| File | Trước → sau |
| --- | --- |
| `garment/simulation/blender/compose_tryon.py` | Mọi mesh trong composition dùng ngưỡng 15% cho đỉnh cần hiệu chỉnh trên 6 cm → `local_parametric` dùng 40%, nguồn khác giữ 15%; hàm validator giữ mặc định 5% cho direct callers. Kiểm tra xuyên sâu sau hiệu chỉnh không đổi. |
| `backend/workers/image_tryon.py` | Log có thể ghi “failed with exit code 0” khi Blender trả 0 nhưng không xuất GLB; thông báo penetration hẹp nghĩa → log phân biệt lỗi exit với thiếu output và dùng thông báo căn chỉnh an toàn tổng quát hơn. Provenance note nay nói dùng reference chiều dài được gửi. |
| `frontend/src/pages/tryon/ImageTryOnPage.tsx` | Hiện Body ID/ô nhập ID và chiều dài thật; chưa có preview body ở bước 1 → ẩn ID, preview body GLB, giữ ID nội bộ trong localStorage, gửi reference ước lượng theo loại trang phục và bỏ trường chiều dài khỏi UI. |
| `frontend/src/viewer/Garment360Viewer.tsx` | Viewer chỉ gắn nhãn trang phục → thêm `subject="body"` để aria label/fallback chính xác và ẩn nút vùng cơ thể trong preview body. |
| `docs/api/api-contract.md` | Mô tả `reference_value_cm` luôn là chiều dài thật → ghi rõ UI ước lượng theo loại, client API khác vẫn có thể gửi số đo thật. |
| `.agents/memory/ACTIVE_CONTEXT.md` | Trạng thái trước đó → ghi nhận các thay đổi M2/M3/M5 và giới hạn kiểm tra. |

## Ảnh hưởng

- **API/schema:** Không đổi endpoint, trường hay kiểu dữ liệu. `reference_value_cm` vẫn là số cm trong khoảng 1–300; UI gửi mốc ước lượng theo loại. Client khác có thể gửi chiều dài đo thật.
- **Đơn vị/hệ trục:** Không đổi; reference dùng cm, GLB dùng mét, Y-up, +Z forward.
- **Mesh/asset:** Không sinh hay sửa asset. Nới guard 40% chỉ cho mode `local_parametric`; bộ kiểm tra xuyên sâu cuối cùng vẫn từ chối scene vượt ngưỡng hiện có.
- **Ảnh hưởng chéo:** M2 thay đổi tiêu chí căn chỉnh; M3 chỉ đổi cách diễn đạt lỗi/provenance note và mô tả API; M5 thay đổi màn image try-on và dùng viewer hiện có. M1/M4 không đổi.
- **Rủi ro đã biết:** Tỉ lệ trang phục không còn được hiệu chỉnh bằng số đo người dùng; chiều dài ước lượng theo category có thể sai với sản phẩm ngoại cỡ hoặc kiểu dáng khác chuẩn. Cảnh vẫn là preview tĩnh, không có cloth simulation hay đánh giá fit.

## Kiểm tra

- Đã rà tĩnh các tham chiếu cũ tới `garmentLength`, nhập Body ID và nhãn “Chiều dài thật” trong `ImageTryOnPage.tsx`; không còn. Mặc định 5% của validator giữ tương thích với ngưỡng unit test hiện có, còn composition truyền ngưỡng cụ thể theo reconstruction mode.
- Chưa chạy automated tests, frontend build hoặc Blender composition trong đợt này.

## Bàn giao

M5 kiểm tra browser preview/tải lại body; M2 chạy lại job `itry_0051f6a57309462d89d71e1548de757b` và xem quality report. Nếu lỗi còn ở guard 40% hoặc kiểm tra xuyên sâu cuối, cần dùng số liệu report để tinh chỉnh mesh placement thay vì tăng ngưỡng tiếp tục. M3 có thể bổ sung nguồn estimate vào provenance contract nếu cần phân biệt rõ giữa estimate và số đo thật ở mọi client.
