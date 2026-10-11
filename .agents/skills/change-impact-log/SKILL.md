---
name: change-impact-log
description: Ghi lại thay đổi và ảnh hưởng sau mỗi đợt agent sửa code, cấu hình hoặc contract của M1–M5, trước khi báo hoàn thành.
---

# CHANGE IMPACT LOG

## Điều kiện kích hoạt

Rule 10 yêu cầu dùng skill này một lần sau mỗi đợt agent sửa code, cấu hình hoặc contract, trước khi báo hoàn thành. Không theo dõi mọi thao tác của con người. Không kích hoạt khi chỉ đọc hoặc đề xuất mà chưa sửa; việc tạo log không tự kích hoạt một log khác.

## Quyền hạn

Giữ nguyên Rule 01–02: không chạy terminal/shell, test hoặc Git; không commit/push. Chỉ dùng Git nếu user cấp quyền chạy Git rõ ràng về sau. Có thể dựa vào file đã đọc, bản diff do công cụ chỉnh file trả về, log/test do user cung cấp; không suy đoán trạng thái local chưa thấy. Chỉ tạo file mới ở docs/change-logs/** theo ngoại lệ hẹp của Rule 10.

## Input

- Vai trò M1/M2/M3/M4/M5 thực hiện, mục đích, thời điểm và phạm vi đợt sửa.
- Danh sách từng file thêm/sửa/xóa, bằng chứng nội dung trước và sau, hàm/trường liên quan. Nếu không biết trạng thái trước, ghi “chưa kiểm tra” thay vì chế nội dung cũ.
- Contract, code consumer, quy ước đơn vị, API/schema/database/asset và kết quả test thực sự quan sát được.
- Owner cần phối hợp, xung đột đã xác nhận, nguy cơ xung đột và bằng chứng cho từng nhận định.

## Quy trình tạo file

1. Chốt một đợt sửa có mục tiêu rõ và tập file thật sự tác động. Bỏ các file chỉ đọc.
2. Kiểm tra từng file và mô tả trước → sau ở mức thay đổi cụ thể, kèm tên hàm, class, trường hoặc mục tài liệu. File mới: trước là chưa tồn tại; file xóa: sau là không còn. Phân biệt thay đổi code thực tế với quy định trong tài liệu.
3. Đánh giá lần lượt API, schema, đơn vị, database, asset, các module khác. “Không ảnh hưởng” chỉ dùng khi đã kiểm tra đủ căn cứ; còn thiếu thì ghi “chưa kiểm tra” và nêu việc cần kiểm tra. Nêu riêng xung đột đã xác nhận và nguy cơ.
4. Ghi test đã chạy và kết quả kèm nguồn log; nếu user chưa chạy hoặc chưa gửi kết quả, ghi “chưa chạy”. Không gọi kế hoạch test là kết quả test.
5. Tạo file UTF-8 mới theo docs/change-logs/YYYYMMDD-HHMMSS-Mx-ten-thay-doi.md, với giờ Asia/Saigon và x là vai trò thực hiện. Với thay đổi liên vai trò do M4 điều phối, dùng M4 và liệt kê tất cả owner chịu ảnh hưởng trong nội dung. Dùng slug khác khi trùng cùng giây; không ghi đè log cũ.
6. Đọc lại nội dung trước khi báo hoàn thành để loại token, password, đường dẫn bí mật, ảnh cá nhân hoặc dữ liệu nhạy cảm. Không tạo log thứ hai chỉ vì file log vừa xuất hiện.

## Nội dung bắt buộc

File log phải có các mục: vai trò và mục đích; từng file thêm/sửa/xóa với trước → sau và hàm/trường liên quan; ảnh hưởng API, schema, đơn vị, database, asset và module khác; owner phối hợp; xung đột xác nhận/nguy cơ với căn cứ và hướng xử lý; test đã chạy/kết quả hoặc chưa chạy; việc còn lại bàn giao. Nếu chưa đủ dữ liệu, ghi rõ “chưa kiểm tra”, dữ liệu còn thiếu và người cần xác nhận.

## Bàn giao

Liên kết file log khi báo hoàn thành, tóm tắt ảnh hưởng chính và việc còn lại. Không gộp tuyên bố an toàn chung chung thay cho bằng chứng.
