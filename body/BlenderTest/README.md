# BodyForge — Web + Blender MPFB Integration

Giao diện web điều chỉnh tỉ lệ cơ thể 3D kết hợp với Blender MPFB, hiển thị GLB trực tiếp trên trình duyệt bằng Three.js.

## Yêu cầu hệ thống

| Phần mềm | Version | Link |
|----------|---------|------|
| **Python** | 3.10+ | https://python.org |
| **Blender** | 4.x | https://blender.org |
| **MPFB2** (tùy chọn) | latest | https://static.makehumancommunity.org/mpfb.html |

> **Note:** Nếu không có MPFB2, hệ thống sẽ tự động dùng **fallback mannequin** (mesh đơn giản).

## Cài đặt & Chạy

### Cách nhanh nhất
```batch
# Chạy file này (tự động cài dependencies + mở browser)
start.bat
```

### Thủ công
```batch
# 1. Tạo virtual env & cài packages
python -m venv backend\venv
backend\venv\Scripts\pip install -r backend\requirements.txt

# 2. Chỉnh đường dẫn Blender (nếu khác mặc định)
# Mở backend\main.py → sửa biến BLENDER_PATH
# HOẶC set environment variable:
set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe

# 3. Khởi động server
backend\venv\Scripts\python backend\main.py

# 4. Mở browser
start http://localhost:8000/app
```

## Cấu trúc dự án

```
BlenderTest/
├── backend/
│   ├── main.py              ← FastAPI server (chạy cái này)
│   └── requirements.txt
│
├── blender_scripts/
│   ├── generate_body.py     ← Chạy trong Blender headless
│   └── apply_clothing.py    ← Apply clothing
│
├── frontend/
│   ├── index.html           ← Giao diện web
│   ├── style.css
│   └── app.js               ← Three.js + API logic
│
├── output/                  ← GLB files được tạo ra
├── assets/clothing/         ← Clothing assets (GLB/OBJ)
└── start.bat                ← Script khởi động nhanh
```

## API Endpoints

```
POST /api/generate          → Tạo body model (trả về job_id)
GET  /api/status/{job_id}   → Poll trạng thái job
GET  /output/{job_id}.glb   → Download GLB file
POST /api/clothing          → Mặc quần áo lên model
GET  /api/clothing/list     → Danh sách clothing có sẵn
GET  /docs                  → Swagger UI (xem full API)
```

## Tích hợp MPFB2

1. Cài MPFB2 addon vào Blender:
   - Mở Blender → Edit → Preferences → Add-ons → Install
   - Tải MPFB2 từ: https://static.makehumancommunity.org/mpfb.html

2. Kích hoạt addon trong Blender preferences

3. Script `generate_body.py` sẽ tự phát hiện MPFB và dùng API thật

## Thêm Clothing Assets

Đặt file `.glb` hoặc `.obj` vào thư mục `assets/clothing/`:
```
assets/clothing/
├── tshirt_basic.glb
├── jeans_straight.glb
└── dress_summer.glb
```

Tên file phải khớp với `clothing_id` trong catalog (`frontend/app.js` → `CLOTHING_CATALOG`).

## Mở rộng thêm

- **Phase 2**: Thêm clothing real-time preview
- **Phase 3**: Tích hợp AI size recommendation
- **Phase 4**: User accounts, save/load models
- **Phase 5**: Animation & video export
