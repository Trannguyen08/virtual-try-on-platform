---
name: m1-body-expert
description: Hướng dẫn agent phụ trách ảnh đầu vào, ước lượng body 3D và số đo M1 theo contract tích hợp của Virtual Try-On Platform.
---

# M1 BODY EXPERT

## Điều kiện kích hoạt

Dùng khi nhiệm vụ giao rõ M1 hoặc đụng tới body/preprocessing/, body/estimation/, body/measurement/ hay đầu ra body cho M3. Đọc Rule 01–02, Rule 06 và Rule 10 trước khi đề xuất sửa file. Khi nhiệm vụ chỉ sửa API hoặc viewer, chuyển cho owner M3/M5 thay vì nhận quyền sửa của họ.

## Hiện trạng đã đối chiếu

Tại nhánh feature/backend-tryon-flow, cấu trúc M1 đã có nhưng các file chức năng được xem còn rỗng. API analyze hiện nhận ảnh và height_cm, kiểm tra dữ liệu ảnh rồi MockProvider tạo bốn số đo synthetic cố định và GLB hình khối. Chưa thấy pipeline MediaPipe, SMPL-X, body reconstruction hay đo cơ thể từ ảnh được nối vào API. Không gọi kết quả mock là phép đo thật.

## Input và output

- Input API hiện tại: ảnh PNG/JPEG hợp lệ, tối đa 5 MiB và 16 triệu pixel; height_cm hữu hạn trong [140, 210]. M3 xử lý upload và validation HTTP; M1 xác định yêu cầu kỹ thuật ảnh cho thuật toán thật cùng M3.
- Output cần bàn giao: số đo height_cm, chest_cm, waist_cm, hip_cm, shoulder_width_cm bằng cm; body mesh GLB mét, tay phải, Y-up, +Z forward, gốc giữa hai bàn chân tại sàn; provenance source/method/notes và confidence nếu có căn cứ.
- Contract đang chạy nằm ở backend/schemas/body.py và docs/api/api-contract.md. Reference M4 data-contract.md có tên trường/hình dạng khác; không tự đổi contract nào.

## Quy trình làm việc

1. Đọc body/** liên quan, schema M3, contract API và test hiện có. Ghi rõ phần rỗng, mock và phần thật.
2. Làm rõ yêu cầu về ảnh, tư thế, số đo và đầu ra nếu contract chưa quyết định. Trình thiết kế trước, chỉ ghi file sau phê duyệt theo Rule 01.
3. Thiết kế từng bước validation ảnh, preprocessing, landmarks, body estimation và đo đạc. Chỉ ghi nhận bước là đã triển khai khi có mã và bằng chứng.
4. Giữ phép đo nội bộ và phép đổi đơn vị nhất quán; khai báo vị trí đổi m/cm. Không âm thầm suy số đo từ height hoặc ảnh nếu chưa có thuật toán được kiểm chứng.
5. Thỏa thuận adapter với M3 qua TryOnProvider, asset registry và backend/schemas/body.py. Trao đổi với M4 về body mesh/số đo cần cho Fit; không tự sửa phần M3/M4.
6. Sau đợt sửa, gọi change-impact-log; ghi thiếu dữ liệu, tác động và người nhận bàn giao.

## Kiểm thử và bàn giao

Đề xuất cho user chạy unit test ở tests/unit/body/ với ảnh hợp lệ, ảnh hỏng, ảnh không có người, số đo biên và mesh sai đơn vị; kiểm thử INT-02 với M3 khi adapter có thật. Đối chiếu output với schema M3 và đo mesh theo khung tọa độ đã chốt. Agent không tự chạy test hoặc Git theo Rule 01–02; ghi kết quả do user cung cấp, nếu thiếu ghi chưa chạy. Bàn giao model/phụ thuộc, giới hạn độ chính xác, schema, asset, test và evidence cho M3/M4.

## Tài liệu kỹ thuật

Tham khảo [landmarks-and-slicing.md](references/landmarks-and-slicing.md), [smplx-specs.md](references/smplx-specs.md) và [edge-cases.md](references/edge-cases.md) khi thiết kế M1; đối chiếu với contract đang chạy trước khi áp dụng.
