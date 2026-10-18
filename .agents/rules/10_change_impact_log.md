# RULE 10: CHANGE IMPACT LOG — ÁP DỤNG M1–M5

## Phạm vi và thứ tự áp dụng

Sau mỗi đợt agent sửa code, cấu hình hoặc contract, trước khi báo hoàn thành, agent phụ trách M1, M2, M3, M4 hoặc M5 bắt buộc gọi skill .agents/skills/change-impact-log/SKILL.md và tạo một log cho đợt đó. Đây là bước trong quy trình agent, không phải hệ thống theo dõi mọi thao tác của con người. Chỉ đọc, thảo luận hoặc đưa đề xuất mà chưa sửa các loại file trên thì không kích hoạt log.

Rule 01 về không chạy terminal/shell, bước phê duyệt và để user chạy test là quy định chung, không bị rule này thay thế. Quy định nhánh feature/fit-ai trong Rule 02, quy chuẩn test Fit/AI của Rule 03, phạm vi chỉnh sửa M4 của Rule 04 và baseline Fit/AI của Rule 05 tiếp tục áp dụng cho M4. Khi user giao rõ M1, M2, M3 hoặc M5, dùng scope tương ứng trong Rule 06–09; không suy rộng quyền M4 sang vai trò đó. Nếu chưa rõ vai trò hoặc quyền sửa file dùng chung, dừng ở đề xuất và xin quyết định theo Rule 01.

Root AGENTS.md hiện mô tả mặc định agent là M4. Yêu cầu giao rõ vai trò khác và phê duyệt rule mới là căn cứ chọn scope vai trò đó; không tự chỉnh AGENTS.md. Việc sửa root directive để hỗ trợ tự chọn vai trò cho mọi phiên cần một thay đổi được duyệt riêng.

## Ngoại lệ hẹp để lưu log

Rule 04 chưa liệt kê docs/change-logs/** trong phạm vi M4. Theo phê duyệt cho bộ rule/skill này, agent M4 được tạo file mới tại docs/change-logs/** chỉ để ghi impact log của đợt sửa; không được dùng ngoại lệ này để sửa code hoặc tài liệu khác ngoài scope M4. Các vai trò còn lại cũng chỉ dùng thư mục đó cho log. Nếu quyền ghi này bị rút hoặc mâu thuẫn với chỉ dẫn mới hơn, nêu rõ xung đột và chờ quyết định; không lặng lẽ bỏ bước.

## Quy trình bắt buộc

1. Chốt danh sách file thật sự đã thêm/sửa/xóa trong đợt, đọc trạng thái trước/sau từ bằng chứng có sẵn. Không tự chạy Git để lấy diff; chỉ kiểm tra Git nếu có quyền rõ ràng từ user.
2. Xác định tác động API, schema, đơn vị, database, asset và module khác; hỏi hoặc ghi “chưa kiểm tra” nếu thiếu dữ liệu. Một khác biệt đã biết là reference JSON M4 và API mock M3 trên feature/backend-tryon-flow không cùng hình dạng; các đợt tích hợp liên quan phải ghi nhận, không tự hòa giải.
3. Gọi skill change-impact-log để tạo một file mới, tên có thời gian Asia/Saigon và mã vai trò thực hiện. Không ghi đè file cũ, không đưa bí mật hoặc dữ liệu cá nhân vào log.
4. Ghi test đã chạy và kết quả dựa trên bằng chứng; nếu agent không được chạy lệnh và user chưa gửi kết quả thì ghi “chưa chạy”. Ghi người nhận bàn giao và việc còn lại.
5. Việc tạo chính file log không kích hoạt log thứ hai.
