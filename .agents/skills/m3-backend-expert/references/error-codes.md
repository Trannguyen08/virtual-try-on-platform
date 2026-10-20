# REFERENCE: SYSTEM ERROR CODES & HTTP STATUS MAPPING (M3)

Bảng mã lỗi chuẩn hóa toàn hệ thống Virtual Try-On cho Module M3.

---

## 1. Bảng Tra cứu Mã lỗi Hệ thống

| HTTP Status | Error Code | Mô tả nguyên nhân | Khuyến nghị cho Client / User |
| :---: | :--- | :--- | :--- |
| **`400`** | `INVALID_IMAGE_FORMAT` | File tải lên không phải định dạng ảnh (JPEG/PNG) | Chọn file ảnh có đuôi `.jpg`, `.jpeg` hoặc `.png`. |
| **`400`** | `INVALID_IMAGE_DIMENSIONS` | Độ phân giải ảnh quá nhỏ ($< 500\text{px}$) | Chụp ảnh rõ nét hơn, độ phân giải tối thiểu $720\text{p}$. |
| **`422`** | `NO_PERSON_FOUND` | Không tìm thấy bóng dáng người trong ảnh | Đứng vào giữa khung hình và chụp lại ảnh toàn thân. |
| **`422`** | `INVALID_BODY_MEASUREMENTS` | Số đo ngoài khoảng nhân trắc học hợp lệ | Nhập lại số đo trong khoảng bình thường ($140 - 210\text{ cm}$). |
| **`404`** | `RESOURCE_NOT_FOUND` | Không tìm thấy `body_id`, `garment_id` hoặc `job_id` | Kiểm tra lại ID đã cung cấp. |
| **`504`** | `JOB_TIMEOUT` | Mô phỏng 3D chạy quá 300 giây | Thử lại với size khác hoặc tải lại trang. |
| **`500`** | `INTERNAL_SIMULATION_ERROR` | Tiến trình Blender hoặc AI gặp sự cố không lường trước | Báo cáo sự cố cho ban quản trị. |
