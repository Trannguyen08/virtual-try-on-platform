# RULE 01: AGENT BEHAVIOR, EXECUTION & COMMUNICATION

## 1. Giới hạn Quyền hạn Tuyệt đối (Execution Boundaries)
Agent chỉ có quyền **READ (Đọc file/thư mục)** và **WRITE (Ghi/Sửa nội dung file)**.

Agent **TUYỆT ĐỐI KHÔNG ĐƯỢC TỰ THỰC THI** các hành động sau trên máy của User:
1. **Không chạy bất kỳ lệnh terminal / shell nào** (không chạy python, pytest, jupyter, node, docker, bash, powershell).
2. **Không chạy bất kỳ lệnh Git nào** (`git commit`, `git push`, `git merge`, `git reset`, `git checkout`, `git clean`, v.v.).
3. **Không tự ý cài đặt package hoặc thay đổi môi trường** (`pip install`, `npm install`, sửa `requirements.txt` khi chưa được duyệt).
4. **Không tự chạy tiến trình nặng** (không tự kích hoạt download dataset, train model, chạy Blender headless).

*Quyền hạn hợp lệ duy nhất về lệnh:*
- Agent được quyền đọc và khám phá codebase tự do để nắm rõ ngữ cảnh.
- Agent **chỉ được đề xuất các câu lệnh dưới dạng Markdown code block** kèm giải thích rõ ràng để **User tự tay copy và chạy** trong terminal.
- Khi ghi file Python, Agent tự căn chỉnh format code chuẩn (indentation, PEP8, import sạch) trực tiếp trong nội dung file ghi ra; **tuyệt đối không chạy công cụ terminal ruff/black**.

---

## 2. Quy trình Tương tác Chuẩn (Strict Operational Workflow)
Mọi công việc phải tuân thủ nghiêm ngặt chu trình sau, không được nhảy cóc:

```text
DISCUSS / CLARIFY (nếu mơ hồ)
  ↓
DESIGN / DECISION PROPOSAL
  ↓
USER APPROVAL ("OK triển khai")
  ↓
IMPLEMENT (Agent ghi file)
  ↓
TEST PLAN (Agent đề xuất lệnh test)
  ↓
USER RUNS TEST (User tự chạy)
  ↓
ANALYZE RESULT (Agent phân tích log/lỗi do User gửi)
  ↓
FIX / ITERATE (Lặp lại nếu cần)
```

### 2.1. Nhánh làm rõ (Clarify First)
- Nếu yêu cầu của User còn mơ hồ, thiếu thông tin (ví dụ: chưa rõ đơn vị `m` hay `cm`, chưa rõ schema dữ liệu, chưa rõ quy tắc nghiệp vụ), Agent **BẮT BUỘC PHẢI DỪNG LẠI ĐỂ HỎI RÕ**, tuyệt đối không tự ý giả định (assumptions) rồi tự code.

### 2.2. Quy định về "Chỉnh sửa nhỏ" (Minor Edits)
- Chỉ được áp dụng tự động cho: **sửa lỗi chính tả (typo) trong comment hoặc docstring**.
- **CẤM** tự ý sửa: không được tự đổi tên hàm/biến public, không được đổi logic nghiệp vụ, không được tự ý sửa mã kiểm thử (test suite) nếu User chưa xác nhận.

---

## 3. Bộ lọc Tư duy trước khi phản hồi (Mindset Filter)
Trước khi xuất bất kỳ câu trả lời nào, Agent phải tự kiểm tra 3 câu hỏi:
1. *Nội dung này có đúng trọng tâm module M4 (Fit & AI) không, hay đang lan man sang việc của M1/M2/M3/M5?*
2. *User đã nói "OK triển khai" chưa mà dám sinh code ghi file? (Nếu chưa: chỉ được trả lời bằng Text giải thích).*
3. *Mình có đang giả định điều gì chưa được kiểm chứng không?*
