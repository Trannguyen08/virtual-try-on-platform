# M3 — Hiển thị nguyên nhân script Blender thất bại trong server log

Thời điểm: 2026-10-19 17:59:43 UTC+7 (Asia/Saigon).

## Mục đích và bằng chứng

User cung cấp job clothing lỗi với exit 0, sau đó `BLENDER_FAILED`.
Code kiểm tra cả exit code và file output, nhưng trước đây không ghi
exception Python của subprocess. Log chưa đủ xác định lỗi geometry gốc.
`MPFB unavailable: False` chỉ là không tìm thấy marker MPFB_UNAVAILABLE.

## File thêm/sửa và trước → sau

- `backend/services/blender_body.py`: thêm `blender_script_error` lấy
  dòng exception Python từ stdout/stderr, giới hạn độ dài, che đường dẫn
  Windows/Unix; không log toàn bộ output hoặc parameters. `run` thêm
  `--python-exit-code 1` trước `--python` và log summary khi output/exit lỗi.
  Trước đây exception Python có thể exit 0 và nguyên nhân bị ẩn; sau đây
  script thất bại sẽ có exit khác 0 và dòng `Blender script error` nếu bắt
  được exception summary. Trường hợp native crash không có summary vẫn
  ghi rõ chưa bắt được exception.
- Thêm `tests/unit/backend/test_blender_job_errors.py`: TC-API-03 hồi quy
  exit 0/1 nhưng thiếu asset, failed job, log nguyên nhân, không trả lỗi
  thô cho client, cờ exit code Python có trong command.
- Thêm file log này.

## API, schema, đơn vị, database, asset và module

Không sửa response/schema/source/method, trạng thái job hay database.
Không sửa geometry M2/M1, hệ trục, đơn vị hoặc file asset. API vẫn trả
thông báo lỗi chung; diagnostic nằm ở log server. M1/M2 nhận nguyên nhân
script sau lần tạo job mới; M5 không cần đổi consumer.

## Xung đột/nguy cơ và owner

Chưa xác định lỗi gốc của áo. Không tự suy rằng MPFB thiếu hoặc sửa
sampler theo phỏng đoán. Summary không thay thế traceback đầy đủ đối với
native crash/lỗi không phải Python. Owner M3 bàn giao log mới cho M1/M2.

## Kiểm thử

Chưa chạy test (Chờ User xác nhận), không chạy Blender/Git/pytest.
Lệnh đề xuất:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/backend/test_blender_job_errors.py -q
```

## Việc còn lại

Khởi động lại backend, tạo lại body/job áo vì job nằm trong RAM, gửi dòng
`Blender script error` mới để sửa đúng lỗi geometry/import/export.
Đợt này chỉ khắc phục chẩn đoán; chưa xác nhận sửa được lỗi tạo áo gốc.
