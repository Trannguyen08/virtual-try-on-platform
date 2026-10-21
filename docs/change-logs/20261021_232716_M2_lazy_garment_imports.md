# Sửa import Trimesh không cần thiết khi Blender đọc catalog

## Vai trò và mục đích

- M2, 2026-10-21 23:27:16, Asia/Saigon (UTC+7).
- Xử lý log User cung cấp: clothing exit 1, ModuleNotFoundError: No module named trimesh. `MPFB unavailable: False` không xác nhận lỗi MPFB.

## File thực tế

| File | Loại | Trước → sau |
| --- | --- | --- |
| garment/__init__.py | Sửa | Eager import size_chart/mesh/simulation khi đọc bất kỳ submodule → __getattr__ nạp module theo public export được truy cập; giữ __all__, identity qua cache và __dir__ |
| tests/unit/garment/test_package_imports.py | Thêm | Chưa có → regression TC-GAR-06 chạy subprocess -S với import blocker, kiểm tra catalog/alignment không phụ thuộc mesh và lightweight public export còn tương thích |
| .agents/memory/ACTIVE_CONTEXT.md | Sửa | Bổ sung nguyên nhân, cách sửa, quyền hạn và trạng thái kiểm thử |
| docs/change-logs/20261021_232716_M2_lazy_garment_imports.md | Thêm | Nhật ký đợt thay đổi |

## Tác động

- API/schema/database: không sửa endpoint, payload hoặc database. Public export Python giữ tên như trước; thời điểm nạp mesh/simulation chuyển sang lúc sử dụng.
- Đơn vị/hệ trục: không sửa mesh, số đo hoặc biến đổi tọa độ.
- Dữ liệu/model/asset: không tạo dữ liệu lớn, không cài package, không sửa môi trường Blender hoặc backend.
- M1/M3: script Blender dùng `garment.mpfb.catalog` không còn kéo mesh/simulation từ root package. Lỗi từ submodule thật sự cần Trimesh vẫn được báo, không fallback hoặc giả kết quả.
- M4/M5: chưa chạy integration, cần xác nhận caller import root và E2E garment. Không sửa code các module này.

## Xung đột và rủi ro

- Đã xác nhận chuỗi import eager trong code và lỗi thiếu Trimesh trong log User. Chưa tái hiện trên Blender thực tế.
- Lazy import thay thời điểm phát hiện dependency thiếu, không loại dependency khỏi các thuật toán cần nó.
- Backend reload có thể làm mất body-builder job bộ nhớ; nếu gặp JOB_NOT_FOUND, tạo model mới trước khi thử lại. Chưa xử lý persistence server trong đợt sửa này.

## Kiểm thử và bàn giao

- Chưa chạy test (chờ User xác nhận/chạy). Quyền chạy build frontend trước đó không được mở rộng thành quyền pytest/Blender.
- Test regression: `python -m pytest tests/unit/garment/test_package_imports.py -q` bằng Python môi trường backend.
- M2/M3/User: chạy regression, các test catalog/external reference hiện có, sau đó thử lại clothing trên cùng Blender đã tạo body. Không coi test import là bằng chứng refit thành công.
