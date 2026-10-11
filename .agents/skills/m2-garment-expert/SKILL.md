---
name: m2-garment-expert
description: Hướng dẫn agent M2 xử lý size chart, mesh trang phục, mô phỏng vải và xuất GLB phù hợp body và API.
---

# M2 GARMENT EXPERT

## Điều kiện kích hoạt

Dùng khi nhiệm vụ giao M2 hoặc liên quan garment/size_chart/, garment/mesh/, garment/simulation/ và GLB áo. Đọc Rule 01–02, Rule 07 và Rule 10. Công thức Fit thuộc M4; phục vụ asset qua HTTP thuộc M3.

## Hiện trạng đã đối chiếu

Trên feature/backend-tryon-flow, file garment/size_chart/charts/shirt.json có sizes rỗng; loader, mesh generator, draping và simulator được xem chưa có nội dung thực thi. Backend đang dùng backend/fixtures/catalog.json với chart synthetic S/M/L/XL và GLB hình hộp cố định. Catalog và mesh mock không chứng minh M2 đã sinh garment theo size hay mô phỏng vải.

## Input và output

- Input dự kiến: size chart có nguồn xác định, thông số garment theo cm, body mesh M1 cùng khung tọa độ và thông số mô phỏng đã duyệt.
- Output dự kiến: catalog/size được validate; garment mesh và draped mesh GLB trong mét, tay phải, Y-up, +Z forward, cùng gốc với body; metadata nguồn và phương pháp để M3 đăng ký asset. JSON/API vẫn dùng số đo cm.
- Contract API hiện tại ở backend/schemas/garment.py, simulation.py và docs/api/api-contract.md. Chỉ dùng tên trường và size có trong contract, trừ khi đã thống nhất thay đổi với M3/M5.

## Quy trình làm việc

1. Kiểm tra nguồn chart, định nghĩa chu vi so với chiều ngang áo, dải size và dữ liệu còn thiếu. Phân biệt chart demo với chart nhà sản xuất.
2. Thiết kế sinh mesh, scale và draping độc lập từng bước. Trình quyết định và xin phê duyệt theo Rule 01 trước khi ghi file.
3. Chuyển đổi hệ tọa độ native Blender khi export, đổi cm sang m đúng một lần ở ranh giới đã xác định; không tự căn giữa mesh riêng khỏi body.
4. Validate topology, GLB, đơn vị, kích thước theo size và asset tồn tại trước khi M3 phát URL. Khi lỗi đầu vào từ M1, báo nguyên nhân thay vì vá ngầm dữ liệu module khác.
5. Phối hợp M3 về catalog/asset registry, M1 về body frame, M4 về mesh/distance phục vụ Fit, M5 về cách tải và hiển thị GLB. Không thay đổi ngưỡng Fit M4.
6. Sau đợt sửa, gọi change-impact-log và bàn giao phụ thuộc, rủi ro.

## Kiểm thử và bàn giao

Đề xuất unit test tests/unit/garment/ cho chart thiếu/sai, kích thước mesh, sai hệ trục và export GLB; INT-03 với M3 cho asset và simulator. Test mô phỏng nặng chỉ do user chạy theo Rule 01, có bằng chứng riêng. Nếu chưa chạy, ghi đúng trạng thái trong log. Bàn giao chart, GLB, quy ước đơn vị, cách tái tạo, giới hạn mô phỏng và tác động tới M1/M3/M4/M5.
