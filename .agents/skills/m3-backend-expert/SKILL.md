---
name: m3-backend-expert
description: Hướng dẫn agent M3 bảo trì API, validation, điều phối, job, database và asset theo contract mock MVP và tiến trình tích hợp module thật.
---

# M3 BACKEND EXPERT

## Điều kiện kích hoạt

Dùng khi nhiệm vụ giao M3 hoặc đụng backend/api/, backend/schemas/, backend/services/, cấu hình backend hay docs/api/. Đọc Rule 01–02, Rule 08 và Rule 10. Không nhận thay thuật toán của M1/M2/M4 hoặc UI của M5.

## Hiện trạng đã đối chiếu

Nhánh feature/backend-tryon-flow có FastAPI create_app, route health/catalog/analyze/fit/jobs/assets, schema Pydantic và response envelope. TryOnOrchestrator kiểm tra ảnh PNG/JPEG, kích thước, MIME và decode; MockProvider dùng fixture cố định. JobManager lưu job trong process và chạy qua BackgroundTasks; asset chỉ cho tên GLB đăng ký. tests/unit/backend/test_backend.py và tests/e2e/mock/test_mock_e2e.py có ca kiểm tra API mock. Chưa thấy database bền vững, queue, adapter M1/M2/M4 thật hoặc đo AI từ ảnh. Không tuyên bố test đã PASS nếu chưa có kết quả chạy.

## Input và output

- GET /health trả status; GET /api/garments trả catalog; POST /api/tryon/analyze nhận multipart image và height_cm; POST /api/tryon/fit nhận body_id, garment_id, size; GET /api/jobs/{job_id} cho polling; GET /api/assets/{asset_name} trả GLB đã đăng ký.
- Thành công dùng data/error=null; lỗi dùng data=null/error với code, message, details. Asset là binary; health ngoài envelope.
- Số đo API là cm, mesh GLB là m, tay phải/Y-up/+Z forward. source/method/notes ghi provenance; mock score/confidence là null. Job có pending, running, completed, failed với result/error nhất quán.
- API schema đang chạy ở backend/schemas/** và docs/api/api-contract.md. Reference JSON M4 khác cấu trúc; giữ riêng đến khi M3–M4–M5 quyết định mapping hoặc version contract.

## Quy trình làm việc

1. Đọc route, schema, provider, tests và docs/api của endpoint liên quan; xác định mock hay module thật.
2. Trình thiết kế và tác động consumer trước khi đổi field, nullability, error, status, asset URL hay storage. Xin phê duyệt theo Rule 01.
3. Thực hiện validation input, xử lý và validation output theo contract; tách adapter thật khỏi MockProvider, giữ provenance chính xác.
4. Nếu làm database/job bền vững, xác định vòng đời, worker, idempotency, cleanup và giới hạn tài nguyên; không suy rằng JobManager hiện đã bền vững.
5. Phối hợp M1/M2/M4 về dữ liệu thật và M5 về API/polling. Chỉ đăng ký asset có quyền truy cập phù hợp, không lộ đường dẫn máy hay lỗi thô.
6. Sau đợt sửa, gọi change-impact-log trước khi báo hoàn thành.

## Kiểm thử và bàn giao

Đề xuất user chạy test backend về schema, validate ảnh, state machine, lỗi và asset; test e2e mock chỉ xác minh HTTP, không phải viewer. Tích hợp module thật cần các INT tương ứng và kiểm tra API contract. Theo Rule 01, agent không tự chạy lệnh; ghi chưa chạy khi thiếu log. Bàn giao OpenAPI/field thay đổi, tác động M5, migration database nếu có, trạng thái mock/real và việc cần owner khác xác nhận.

## Tài liệu kỹ thuật

Tham khảo [api-endpoints-and-schemas.md](references/api-endpoints-and-schemas.md), [async-job-flow.md](references/async-job-flow.md) và [error-codes.md](references/error-codes.md) khi thiết kế M3; đối chiếu với API đang chạy trước khi áp dụng.
