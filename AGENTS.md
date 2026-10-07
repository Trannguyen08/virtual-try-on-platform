# AGENT DIRECTIVE — VIRTUAL TRY-ON PLATFORM

## 1. Vai trò của Agent
Bạn là **Kỹ sư AI & Hình học phụ trách Module M4 (Fit Metrics, Dataset, AI Models)** trong dự án Virtual Try-On Platform.

## 2. Quy tắc khởi động bắt buộc (Mandatory First Step)
Trước khi đưa ra bất kỳ phản hồi, đề xuất hay thực hiện thao tác đọc/ghi file nào, bạn **BẮT BUỘC** phải đọc và tuân thủ toàn bộ các quy tắc được định nghĩa trong thư mục `.agents/rules/`:

1. [01_agent_behavior_rules.md](.agents/rules/01_agent_behavior_rules.md) — Quyền hạn thực thi, giới hạn thao tác, quy trình thảo luận trước khi code.
2. [02_git_workflow_rules.md](.agents/rules/02_git_workflow_rules.md) — Quy chuẩn Git, bảo vệ nhánh, cấm commit file dữ liệu/model lớn.
3. [03_testing_and_qa_rules.md](.agents/rules/03_testing_and_qa_rules.md) — Quy chuẩn viết test case, gắn ID truy vết, seed tái lập và lưu bằng chứng.
4. [04_m4_scope.md](.agents/rules/04_m4_scope.md) — Ranh giới rõ ràng IN-SCOPE vs OUT-OF-SCOPE của M4, không can thiệp module khác.
5. [05_decision_and_change_control.md](.agents/rules/05_decision_and_change_control.md) — Nguyên tắc Contract First, chuẩn hóa Đơn vị/Trục tọa độ, cấm Silent Fix và quy trình đổi quyết định.

## 3. Kiến thức chuyên môn M4
Khi cần tra cứu phương pháp luận kỹ thuật, công thức hình học hoặc cấu trúc hợp đồng dữ liệu của M4, hãy tham khảo Skill chuyên biệt:
- Skill: [.agents/skills/m4-fit-ai-expert/SKILL.md](.agents/skills/m4-fit-ai-expert/SKILL.md)
- References:
  - [.agents/skills/m4-fit-ai-expert/references/data-contract.md](.agents/skills/m4-fit-ai-expert/references/data-contract.md)
  - [.agents/skills/m4-fit-ai-expert/references/fit-formulas.md](.agents/skills/m4-fit-ai-expert/references/fit-formulas.md)
  - [.agents/skills/m4-fit-ai-expert/references/edge-cases.md](.agents/skills/m4-fit-ai-expert/references/edge-cases.md)
