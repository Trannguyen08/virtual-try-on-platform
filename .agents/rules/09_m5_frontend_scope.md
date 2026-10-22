# RULE 09: M5 FRONTEND — PHẠM VI VÀ BÀN GIAO

## Áp dụng và hiện trạng

Áp dụng khi yêu cầu giao rõ vai trò M5. Rule 01–02 về quyền chạy lệnh, phê duyệt và Git vẫn áp dụng; ranh giới mã M4 trong Rule 04 không tự trở thành ranh giới M5.

Nhánh feature/backend-tryon-flow đã có giao diện upload/chọn áo/xử lý/kết quả, hàm gọi analyze và fit rồi polling trong frontend/src/api/tryonApi.ts, cùng viewer Three.js dựng hình minh họa trong InteractiveViewer3DStep.tsx. API client cũng có fallback mock phía trình duyệt. Các file useTryOn.ts, useJobPolling.ts, ModelLoader.ts, Heatmap.ts và Scene.tsx được xem vẫn là placeholder; chưa có loader GLB và heatmap hoàn chỉnh từ những file đó. Không trình bày hình minh họa, điểm mock hoặc progress giả là suy luận AI/mô phỏng thật.

## Phạm vi được sửa

- frontend/**: giao diện, gọi API, polling, state, viewer, hiển thị số đo/fit và test frontend.
- docs/report/evidence/frontend/**.
- File rule và skill riêng của M5 trong .agents/**; docs/change-logs/** chỉ cho impact log theo Rule 10.
- docs/api/** hoặc shared contract chỉ được sửa khi M3 và owner liên quan đã thống nhất.

## Ngoài trách nhiệm

M5 không sở hữu đo body M1, mesh/mô phỏng M2, route/job/database M3 hoặc công thức Fit/AI M4. Viewer không tự đổi hệ trục hoặc bịa confidence/score để bù dữ liệu thiếu.

## Contract và file cần phối hợp

- M3 sở hữu docs/api/api-contract.md và backend/schemas/**. API hiện dùng envelope data/error, số đo cm, size S/M/L/XL, score/confidence nullable, provenance source/method/notes, job pending/running/completed/failed và URL GLB tương đối theo backend origin.
- M5 phải hiển thị rõ mock/mixed; null hiển thị “chưa có”. Job failed nằm trong data.error của response GET job. Không coi label mock hay client fallback là tư vấn size thực.
- GLB dùng mét, tay phải, Y-up, +Z forward. Chọn tryon_mesh hoặc cặp body_mesh/garment_mesh; không chồng cả ba. M2/M3 cần phối hợp khi URL/asset hoặc cách xuất GLB thay đổi.
- Tài liệu contract M4 có hình dạng JSON khác API hiện tại; chờ M3–M4 thống nhất rồi mới đổi kiểu dữ liệu M5. Không tự diễn giải lại công thức Fit.

## Điều kiện hoàn thành

Luồng thành công, lỗi, timeout và job failed được kiểm tra; dữ liệu mock/real và null thể hiện trung thực. Viewer không làm sai đơn vị hay chồng mesh, có xử lý asset thiếu. Test frontend phù hợp và kiểm tra tích hợp với API M3 được user chạy theo Rule 01, hoặc ghi rõ chưa chạy. Bàn giao tương thích API và gọi skill change-impact-log trước khi báo hoàn thành đợt sửa.
