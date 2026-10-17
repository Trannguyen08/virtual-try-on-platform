# CHANGE IMPACT LOGS (M1 - M5)

Thư mục lưu trữ các bản ghi nhật ký đánh giá tác động thay đổi (**Change Impact Logs**) được tạo tự động bởi Agent sau mỗi đợt chỉnh sửa code, cấu hình hoặc hợp đồng dữ liệu theo quy định tại:
- Rule: [.agents/rules/common/05_change_impact_log.md](../../.agents/rules/common/05_change_impact_log.md)
- Skill: [.agents/skills/change-impact-log/SKILL.md](../../.agents/skills/change-impact-log/SKILL.md)

## Quy tắc Đặt tên File
- Định dạng: `YYYYMMDD_HHMMSS_<ROLE>_<short_description>.md`
- Thời gian: Lấy theo múi giờ **Asia/Saigon (UTC+7)**.
- Role: `M1`, `M2`, `M3`, `M4`, hoặc `M5`.
