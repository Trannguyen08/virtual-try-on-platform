# RULE 06: M1 BODY — PHẠM VI VÀ BÀN GIAO

## Áp dụng và hiện trạng

Áp dụng khi yêu cầu giao rõ vai trò M1. Giới hạn chạy lệnh, phê duyệt và Git trong Rule 01–02 vẫn có hiệu lực. Rule 04 và các quyết định Fit/AI trong Rule 05 dành cho M4; M1 không lấy chúng làm quyền sửa mã M4.

Đối chiếu nhánh feature/backend-tryon-flow: body/preprocessing/, body/estimation/ và body/measurement/ đã có cấu trúc nhưng các file chức năng được xem còn rỗng; tests/unit/body/test_body.py và INT-02 cũng chưa có ca kiểm thử. Backend hiện kiểm tra ảnh rồi MockProvider trả số đo cố định, không đo từ ảnh hay dựng body thật. Mọi mô tả về MediaPipe, SMPL-X và phép đo ảnh dưới đây là mục tiêu triển khai, không phải tính năng đã có.

## Phạm vi được sửa

- body/**: nạp, kiểm tra, tiền xử lý ảnh; ước lượng dáng người bằng MediaPipe hoặc phương pháp được duyệt; dựng mesh body; tính số đo.
- tests/unit/body/** và docs/report/evidence/body/**.
- tests/integration/INT-02/** khi phối hợp với M3 để thử đường nối Body–API.
- File rule và skill riêng của M1 trong .agents/**; docs/change-logs/** chỉ để ghi impact log theo Rule 10.

Không tự sửa file dùng chung hoặc module khác chỉ vì cần tích hợp; trình bày thay đổi contract và xin phối hợp owner trước.

## Ngoài trách nhiệm

M1 không sở hữu size chart, mesh và mô phỏng vải của M2; điểm Fit/AI của M4; FastAPI, database, job và asset registry của M3; giao diện và viewer của M5.

## Contract và file cần phối hợp

- M3 sở hữu backend/schemas/body.py, backend/services/orchestrator.py, docs/api/api-contract.md và adapter TryOnProvider. M1 bàn giao kết quả để M3 nối vào provider, không tự sửa API.
- shared/interfaces/body.py và shared/constants/ hiện là khung; mọi định nghĩa chung phải thống nhất với M3 và các consumer trước khi ghi.
- API đang nhận ảnh PNG/JPEG tối đa 5 MiB, 16 triệu pixel và height_cm 140–210. Số đo JSON là cm. Mesh GLB theo contract M3 dùng mét, tay phải, Y-up, +Z forward, gốc tại sàn. Không tự đổi đơn vị hoặc suy số đo từ ảnh nếu chưa thực hiện phép đo thật.
- Reference M4 trong .agents/skills/m4-fit-ai-expert/references/data-contract.md có cấu trúc JSON khác API M3 hiện tại. Ghi nhận khác biệt và phối hợp M3–M4 trước khi tích hợp; không sửa ngầm một phía.

## Điều kiện hoàn thành

Đầu vào lỗi được xử lý có lý do rõ ràng; số đo và mesh có nguồn gốc, phương pháp, đơn vị và confidence phù hợp; kết quả body thật không gắn nhãn mock. Có unit test M1 và kiểm thử contract INT-02 theo kế hoạch, hoặc ghi rõ chưa chạy theo Rule 01. Bàn giao giới hạn dữ liệu, phụ thuộc M3/M4 và bằng chứng kiểm thử. Gọi skill change-impact-log trước khi báo hoàn thành đợt sửa.
