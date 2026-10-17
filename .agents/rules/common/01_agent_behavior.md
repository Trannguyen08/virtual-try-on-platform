# RULE 01: AGENT BEHAVIOR, EXECUTION & COMMUNICATION (COMMON)

> **Phạm vi áp dụng:** Áp dụng bắt buộc cho toàn bộ Agent ở mọi Role (M1, M2, M3, M4, M5).

---

## 1. Giới hạn Quyền hạn Tuyệt đối (Execution Boundaries)
Agent chỉ có quyền **READ (Đọc file/thư mục)** và **WRITE (Ghi/Sửa nội dung file)**.

Agent **TUYỆT ĐỐI KHÔNG ĐƯỢC TỰ THỰC THI** các hành động sau trên máy của User:
1. **Không chạy bất kỳ lệnh terminal / shell nào** (không tự chạy `python`, `pytest`, `jupyter`, `node`, `npm`, `docker`, `bash`, `powershell`).
2. **Không chạy bất kỳ lệnh Git nào** (`git commit`, `git push`, `git merge`, `git reset`, `git checkout`, `git clean`, v.v.).
3. **Không tự ý cài đặt package hoặc thay đổi môi trường** (`pip install`, `npm install`, tự sửa `requirements.txt`/`package.json` khi chưa được duyệt).
4. **Không tự chạy tiến trình nặng** (không tự kích hoạt download dataset, train model, render Blender headless).

*Quy chuẩn tương tác về câu lệnh:*
- Agent được quyền đọc và khám phá codebase tự do để nắm rõ ngữ cảnh.
- Agent **chỉ được đề xuất các câu lệnh dưới dạng Markdown code block** kèm giải thích rõ ràng để **User tự tay copy và chạy** trong terminal.
- Khi ghi file Python/TypeScript/CSS, Agent tự căn chỉnh format code chuẩn (indentation, PEP8, import sạch) trực tiếp trong nội dung file ghi ra; **tuyệt đối không chạy công cụ terminal ruff/black/prettier**.

---

## 2. Quy trình Tương tác Chuẩn (Operational Workflow)
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
- Nếu yêu cầu của User chưa rõ ràng (ví dụ: chưa rõ đơn vị cm hay m, chưa rõ dùng mock hay dữ liệu thật), Agent **BẮT BUỘC HỎI LẠI** trước khi đưa ra phương án.
- Không tự suy diễn các quyết định mang tính kiến trúc hệ thống.

### 2.2. Nhánh đề xuất (Propose First)
- Trước khi tạo/sửa đổi code, Agent phải tóm tắt:
  1. Mục đích thay đổi.
  2. Các file sẽ bị ảnh hưởng.
  3. Phương pháp kỹ thuật hoặc thuật toán áp dụng.
  4. Tác động tới hợp đồng (Contract) với các module khác (nếu có).

### 2.3. Trình bày kết quả & Báo cáo
- Báo cáo ngắn gọn, trọng tâm, dùng tiếng Việt chuẩn mực.
- Cấm dùng ký hiệu LaTeX phức tạp (`$\rightarrow$`, `$\le$`) trong tin nhắn và tài liệu Markdown; thay bằng ký tự Unicode chuẩn (`→`, `<=`, `≈`).
- Dẫn link file clickable theo chuẩn markdown (`[tên_file](file:///đường_dẫn_tuyệt_đối)`).
