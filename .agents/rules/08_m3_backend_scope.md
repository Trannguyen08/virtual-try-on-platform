# RULE 08: M3 BACKEND — PHẠM VI VÀ BÀN GIAO

## Áp dụng và hiện trạng

Áp dụng khi yêu cầu giao rõ vai trò M3. Rule 01–02 về quyền chạy lệnh, phê duyệt, không commit/push và bảo vệ dữ liệu vẫn áp dụng; tên nhánh feature/fit-ai trong Rule 02 là quy định M4, không tự áp cho M3.

Nhánh feature/backend-tryon-flow đã triển khai API mock: GET /health, GET /api/garments, POST /api/tryon/analyze, POST /api/tryon/fit, GET /api/jobs/{job_id} và GET /api/assets/{asset_name}. Pydantic schema, envelope data/error, validate ảnh, BackgroundTasks, job store trong process và asset allowlist đã có mã và test. MockProvider trả số đo, nhãn và GLB fixture cố định; chưa gọi M1/M2/M4 thật. Database bền vững, worker/job queue và adapter thật là dự kiến, không mô tả là đã có.

## Phạm vi được sửa

- backend/**: API, schema, validation, orchestration, cấu hình, job, database và asset khi nhiệm vụ đã được duyệt.
- tests/unit/backend/** và docs/report/evidence/backend/**.
- docs/api/** cho contract M3, nhưng thay đổi schema hoặc hành vi công khai cần thông báo và thống nhất với consumer trước khi triển khai.
- tests/integration/** và tests/e2e/** chỉ ở ca do M3 điều phối và có owner module liên quan phối hợp.
- File rule và skill riêng của M3 trong .agents/**; docs/change-logs/** chỉ cho impact log theo Rule 10.

## Ngoài trách nhiệm

M3 không tự viết thuật toán Body M1, Garment M2, Fit/AI M4 hoặc giao diện M5. Không biến mock thành kết quả thật bằng cách đổi source hoặc method.

## Contract và file cần phối hợp

- docs/api/api-contract.md và backend/schemas/** là contract API MVP đang triển khai; frontend/src/api/tryonApi.ts và frontend/src/api/types.ts là consumer M5. Sửa field, trạng thái job, mã lỗi, URL asset hoặc quy tắc null cần phối hợp M5.
- M1 bàn giao body và số đo; M2 bàn giao garment/draped GLB; M4 bàn giao điểm Fit/AI. Adapter phải validate input/output và giữ provenance source/method/notes cho từng thành phần.
- M4 data-contract.md ghi mẫu JSON khác envelope và trường của API MVP. Đây là khác biệt đã xác nhận giữa tài liệu M4 và API M3; cần quyết định contract tích hợp cùng M4/M5 trước khi nối thật. Không âm thầm map làm mất dữ liệu hoặc đổi công thức M4.
- shared/interfaces/** hiện là khung; chỉ sửa theo quyết định liên module. Không đưa bí mật, ảnh người dùng, đường dẫn nội bộ hoặc lỗi thô vào response/log.

## Điều kiện hoàn thành

OpenAPI, response schema, mã lỗi, quyền truy cập asset và trạng thái job khớp contract đã thống nhất; mock vẫn được ghi rõ. Có test route/schema, lỗi, job và asset phù hợp; với database hoặc queue mới cần kiểm tra vòng đời và tính bền vững. Theo Rule 01, agent đề xuất lệnh để user chạy và ghi rõ test nào chưa chạy. Bàn giao consumer bị ảnh hưởng và gọi skill change-impact-log trước khi báo hoàn thành đợt sửa.
