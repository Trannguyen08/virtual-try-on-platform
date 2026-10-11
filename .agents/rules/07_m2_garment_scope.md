# RULE 07: M2 GARMENT — PHẠM VI VÀ BÀN GIAO

## Áp dụng và hiện trạng

Áp dụng khi yêu cầu giao rõ vai trò M2. Rule 01–02 về quyền chạy lệnh, phê duyệt và Git vẫn áp dụng. Rule 04 và Fit Score trong Rule 05 thuộc M4.

Trên nhánh feature/backend-tryon-flow, garment/size_chart/charts/shirt.json chỉ có bảng sizes rỗng; garment_loader.py, mesh_generator.py và các file simulation được xem còn rỗng. Catalog và ba GLB demo đang do backend/fixtures/ cung cấp, với hình khối cố định không thay đổi theo size. Size chart thật, mesh trang phục theo size và mô phỏng vải là phần dự kiến.

## Phạm vi được sửa

- garment/**: nạp và kiểm tra size chart; sinh, scale và xuất mesh; mô phỏng, draping và batch simulation.
- tests/unit/garment/** và docs/report/evidence/garment/**.
- tests/integration/INT-03/** khi phối hợp với M3 cho luồng Simulator–API.
- File rule và skill riêng của M2 trong .agents/**; docs/change-logs/** chỉ cho impact log theo Rule 10.

## Ngoài trách nhiệm

M2 không sở hữu dựng body và số đo M1, chấm Fit/AI M4, route/job/asset serving M3 hoặc viewer M5. Không sửa backend/fixtures/catalog.json để giả làm size chart M2 khi chưa phối hợp M3.

## Contract và file cần phối hợp

- backend/schemas/garment.py, backend/schemas/simulation.py, backend/services/mock_provider.py, backend/services/assets.py và docs/api/api-contract.md do M3 quản lý; thay đổi trường, URL hoặc danh mục size cần M3 duyệt.
- shared/interfaces/garment.py và shared/interfaces/simulator.py hiện là khung; thống nhất đầu vào, đầu ra với M1, M3, M4 trước khi dùng chung.
- API MVP hiện dùng size S/M/L/XL; số đo chart JSON bằng cm. Body, garment và draped GLB phải cùng khung mét, tay phải, Y-up, +Z forward; M2 chuyển hệ Blender khi export. Không tự đặt lại ngưỡng vùng hay trọng số Fit của M4.
- M5 tiêu thụ asset GLB qua URL backend; chỉ bàn giao asset đã được M3 đăng ký và còn tồn tại.

## Điều kiện hoàn thành

Nguồn chart được nêu rõ là nhà sản xuất hay synthetic; từng size có số đo hợp lệ. Mesh có đơn vị, hệ trục và kích thước kiểm chứng được; mô phỏng lỗi không bị ghi thành kết quả thật. Có unit test M2 và kiểm thử INT-03 khi sẵn sàng, hoặc ghi rõ chưa chạy. Bàn giao chart/GLB, giới hạn mô phỏng, tác động M1/M3/M4/M5 và bằng chứng. Gọi skill change-impact-log trước khi báo hoàn thành đợt sửa.
