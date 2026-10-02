# 📖 V-FIT 3D — QUY TẮC PHÁT TRIỂN & HƯỚNG DẪN NÂNG CẤP DỰ ÁN

> Tài liệu chuẩn dành cho Developer và AI Assistant để duy trì, bảo trì và nâng cấp nền tảng **Virtual Try-On Platform**.

---

## 1. KIẾN TRÚC TỔNG THỂ & SƠ ĐỒ KẾT HỢP (DUAL-ENGINE)

Hệ thống kết hợp sức mạnh giữa **Giao diện người dùng thời trang cao cấp (React Vite TS)** và **Bộ máy sinh giải phẫu 3D (Blender MPFB)**:

```text
       ┌─────────────────────────────────────────────────────────────┐
       │                 FRONTEND (React 18 + Vite)                  │
       │    Haute Couture Luxury UI • Single Source of Truth         │
       └──────┬───────────────────────┬──────────────────────────────┘
              │                       │
     [Offline / Vercel]        [Local Dev / Production API]
              │                       │
              ▼                       ▼
   ┌──────────────────────┐   ┌──────────────────────────────────────┐
   │  Static 3D Library   │   │  Blender MPFB FastAPI Backend        │
   │  (/public/models/)   │   │  (body/BlenderTest/backend/main.py)  │
   │  • body_default.glb  │   │  • POST /api/generate                │
   │  • body_athletic.glb │   │  • GET  /api/status/{job_id}         │
   │  • body_curvy.glb    │   │  • Headless Blender MPFB generator   │
   │  • body_female.glb   │   │  • Real-time .glb mesh export        │
   └──────────┬───────────┘   └──────────────────┬───────────────────┘
              │                                  │
              └──────────────────┬───────────────┘
                                 │
                                 ▼
              ┌─────────────────────────────────────┐
              │     Three.js WebGL Interactive      │
              │  • GLTFLoader 360° Inspection       │
              │  • Layer Switching (Body / Garment) │
              │  • Wireframe & Studio/Warm Lighting │
              │  • Photorealistic 4K Before/After   │
              └─────────────────────────────────────┘
```

---

## 2. HƯỚNG DẪN KHỞI CHẠY HỆ THỐNG CỤC BỘ

### 2.1. Chạy Frontend (React Vite)
```bash
cd frontend
npm install
npm run dev
# Mở trình duyệt tại: http://localhost:5173
```

### 2.2. Chạy Blender 3D Morphing Backend (Tùy chọn)
Nếu bạn có cài đặt Blender (hỗ trợ addon MPFB) trên máy tính:
```bash
cd body/BlenderTest
# Tạo virtual environment và cài đặt requirements
pip install -r requirements.txt
# Khởi động FastAPI server
python backend/main.py
# Server chạy tại: http://localhost:8000 (Swagger docs: http://localhost:8000/docs)
```
> **Lưu ý:** Frontend được thiết kế với cơ chế **Graceful Fallback**. Nếu không bật backend, ứng dụng vẫn hoạt động 100% đầy đủ chức năng với kho 3D mesh có sẵn trong `frontend/public/models/`.

---

## 3. QUY TRÌNH NÂNG CẤP & MỞ RỘNG TÍNH NĂNG

### 3.1. Thêm một vóc dáng người mẫu 3D mới
1. Chuẩn bị file `.glb` đã tối ưu (kích thước khuyến nghị: < 1.5MB).
2. Sao chép file vào thư mục: `frontend/public/models/<ten_file>.glb`.
3. Mở file [bodyPresets.ts](file:///c:/6451071003/Repo%20GitHub/virtual-try-on-platform/frontend/src/data/bodyPresets.ts) và thêm preset mới vào mảng `BODY_PRESETS`:
   ```typescript
   {
     id: 'petite',
     name: 'Khánh Vy (Petite)',
     gender: 'female',
     height: 158,
     weight: 45,
     stats: '1m58 • 45kg',
     description: 'Dáng người nhỏ nhắn, vòng eo thon gọn chuẩn vóc dáng Á Đông.',
     img: 'https://images.unsplash.com/...',
     glbModelUrl: '/models/<ten_file>.glb',
     proportions: {
       shoulder_width: 0.3,
       waist: 0.25,
       hips: 0.35,
       chest: 0.3,
       belly: 0.05,
       muscle_tone: 0.15,
       leg_length: 0.5,
       arm_length: 0.45,
       buttocks: 0.35,
     },
   }
   ```
4. Giao diện tại Bước 1 (Upload) và Bước 3 (Confirm) sẽ tự động nhận diện và hiển thị mẫu mới mà không cần sửa đổi thêm code logic.

### 3.2. Thêm sản phẩm thời trang mới vào Catalog
1. Mở file [mockProducts.ts](file:///c:/6451071003/Repo%20GitHub/virtual-try-on-platform/frontend/src/data/mockProducts.ts).
2. Thêm item mới với đầy đủ thông tin: `id`, `name`, `brand`, `category`, `price`, `imageUrl`, `description`, `sizes`, `colors`, `fabric`, `features`.
3. Sản phẩm mới sẽ tự động hiển thị trên Trang chủ, Trang danh mục, Modal xem chi tiết và Luồng thử đồ.

### 3.3. Thêm thanh trượt giải phẫu MPFB mới
1. Mở [bodyPresets.ts](file:///c:/6451071003/Repo%20GitHub/virtual-try-on-platform/frontend/src/data/bodyPresets.ts) và thêm thuộc tính vào interface `BodyProportions`.
2. Mở [BodyMorphingPanel.tsx](file:///c:/6451071003/Repo%20GitHub/virtual-try-on-platform/frontend/src/components/tryon/BodyMorphingPanel.tsx) và thêm thanh slider mới tương ứng.
3. Cập nhật hàm `generateBodyWithBlender` trong [tryonApi.ts](file:///c:/6451071003/Repo%20GitHub/virtual-try-on-platform/frontend/src/api/tryonApi.ts) để gửi trường này tới FastAPI backend.

---

## 4. QUY CHUẨN DEPLOY VERCEL & SỬA LỖI THƯỜNG GẶP

### 4.1. Lỗi trang 404 khi truy cập hoặc refresh trên Vercel
- **Nguyên nhân:** React là Single Page Application (SPA). Khi người dùng refresh ở route con (ví dụ: `/try-on`, `/catalog`), Vercel tìm file vật lý tương ứng thay vì đưa về `index.html`.
- **Giải pháp:** File `vercel.json` ở thư mục gốc bắt buộc phải có cấu hình rewrites:
  ```json
  {
    "buildCommand": "cd frontend && npm install && npm run build",
    "outputDirectory": "frontend/dist",
    "rewrites": [
      {
        "source": "/(.*)",
        "destination": "/index.html"
      }
    ]
  }
  ```

### 4.2. Lỗi TypeScript / Vite Build khi Deploy
Trước khi push code lên GitHub, luôn chạy lệnh kiểm tra build cục bộ:
```powershell
cmd.exe /c "npm run build"
```
Nếu có lỗi Type checking, sửa ngay lập tức tại local trước khi commit.

### 4.3. Quản lý nhánh Git (Branching Policy)
- Luôn tạo nhánh tính năng từ `feature/*` hoặc `develop`.
- Khi kết hợp các nhánh (ví dụ `feature/body` vào `feature/frontend-*`), sử dụng:
  ```bash
  git fetch origin
  git pull origin <ten_nhanh>
  ```
- Luôn kiểm tra `git status` để bảo đảm không để sót file conflict hoặc untracked files.

---

## 5. BẢNG MÀU THƯƠNG HIỆU & DESIGN SYSTEM (HAUTE COUTURE)

| Biến CSS Token | Mã màu Hex | Ý nghĩa sử dụng |
| :--- | :--- | :--- |
| `--vfit-primary` | `#080a61` | Xanh hoàng gia sẫm — Màu thương hiệu chính |
| `--vfit-primary-container` | `#0c0e7a` | Tông nhấn đậm cho CTA chính và tiêu đề |
| `--vfit-focus-ring` | `#3d7eff` | Xanh Electric — Trạng thái active, viền focus |
| `--vfit-surface` | `#fbf8ff` | Nền kem ngà Haute Couture sang trọng |
| `--vfit-surface-card` | `#ffffff` | Thẻ bề mặt nổi bật |
| `--vfit-on-surface` | `#191b23` | Màu chữ chính, độ tương phản cao |
| `--vfit-secondary` | `#595e72` | Màu chữ phụ, mô tả phụ trợ |
| `--vfit-border-subtle` | `rgba(8,10,97,0.08)` | Viền mờ tinh tế phân tách nội dung |

---

## 6. LỘ TRÌNH PHÁT TRIỂN TIẾP THEO (ROADMAP)

- [x] **Phase 1: Luxury UI/UX Design System:** 13 màn hình Haute Couture hoàn chỉnh.
- [x] **Phase 2: Try-On Flow & Interactive 3D Viewer:** Tải ảnh, chọn đồ, xác nhận, mô phỏng Three.js 360°, trước/sau 4K.
- [x] **Phase 3: Try-On History & Product Detail Modal:** Lưu trữ LocalStorage, xem lại lịch sử, so sánh 2 phiên thử đồ.
- [x] **Phase 4: Blender MPFB Morphing Integration:** Tích hợp 4 preset vóc dáng 3D thực tế, thanh trượt giải phẫu cơ thể học, API sinh mesh thời gian thực.
- [ ] **Phase 5: Real-time Cloth Physics Simulation:** Tích hợp bộ giải vải thời gian thực (Verlet integration / GPU cloth physics trên Three.js).
- [ ] **Phase 6: Multi-garment Layering:** Hỗ trợ phối nhiều lớp trang phục đồng thời (Áo sơ mi + Áo khoác Blazer + Quần âu).
