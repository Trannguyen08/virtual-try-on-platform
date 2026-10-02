# AGENTS.md — AI & Developer Operating Rules

> Quy chuẩn kiến trúc, quy tắc phát triển và hướng dẫn nâng cấp hệ thống **Virtual Try-On Platform (V-Fit 3D)**.
> Tài liệu này được thiết lập để mọi kỹ sư và AI Coding Agent tuân thủ khi mở rộng tính năng.

---

## 1. TỔNG QUAN HỆ THỐNG & TRIẾT LÝ THIẾT KẾ

Dự án áp dụng mô hình **Dual-Engine Hybrid Architecture (Frontend-First)**:

1. **Frontend Core (`/frontend`) — Nền tảng trung tâm (Single Source of Truth):**
   - Công nghệ: **React 18 + TypeScript + Vite + Three.js (WebGL)**.
   - Đảm nhiệm: Toàn bộ trải nghiệm người dùng Haute Couture, điều hướng luồng thử đồ 4 bước, catalog thời trang, lịch sử thử đồ, so sánh side-by-side, và tương tác 3D WebGL xoay 360°.
   - **Quy tắc Vàng (Frontend Standalone):** Ứng dụng phải hoạt động độc lập và mượt mà trên Vercel hoặc bất kỳ static CDN nào mà không bắt buộc có Blender server chạy nền (thông qua kho mẫu 3D có sẵn tại `public/models/` và mock engine fallback).

2. **Body Morphing Engine (`/body/BlenderTest`) — Máy sinh mô hình sinh trắc học:**
   - Công nghệ: **FastAPI + Blender Headless + MPFB2 (MakeHuman Plugin for Blender)**.
   - Đảm nhiệm: Nhận tham số giải phẫu cơ thể học (`BodyParamsModel`: vai, ngực, eo, hông, cơ bắp, tone da), sinh lưới 3D thực tế và xuất file `.glb`.
   - Khi chạy cục bộ (`http://localhost:8000`), Frontend tự động kết nối qua `POST /api/generate` và cập nhật mesh 3D thời gian thực.

---

## 2. QUY CHUẨN CẤU TRÚC THƯ MỤC

```text
virtual-try-on-platform/
├── AGENTS.md                  # Hướng dẫn quy tắc cho AI & Developers (File này)
├── PROJECT_RULES.md           # Sổ tay chi tiết & roadmap phát triển
├── vercel.json                # Cấu hình build & routing Vercel Monorepo
├── frontend/                  # [CORE] React Vite Application
│   ├── public/
│   │   ├── models/            # 3D GLB Models (body_default, athletic, curvy, female_mpfb)
│   │   └── favicon.svg
│   ├── src/
│   │   ├── api/               # API clients (tryonApi.ts, types.ts)
│   │   ├── components/        # Reusable UI components
│   │   │   ├── layout/        # Navbar, Footer
│   │   │   ├── tryon/         # Stepper, UploadStep, BodyMorphingPanel, Confirm, 3D Viewer
│   │   │   ├── catalog/       # ProductCard, FilterSidebar, DetailModal
│   │   │   └── history/       # HistoryCard, CompareModal, StatsBar, Toolbar
│   │   ├── data/              # Mock products, presets (bodyPresets.ts, mockProducts.ts)
│   │   ├── pages/             # Route pages (Home, Catalog, TryOn, History)
│   │   ├── services/          # LocalStorage persistence (historyStorage.ts)
│   │   └── styles/            # Luxury Haute Couture tokens & component CSS
│   └── package.json
├── body/                      # [3D ENGINE] Blender MPFB Morphing Backend
│   └── BlenderTest/
│       ├── backend/main.py    # FastAPI queue & job manager
│       ├── blender_scripts/   # Headless Python scripts for Blender
│       └── output/            # Generated .glb mesh files
└── backend/                   # [TRY-ON PIPELINE] Core ML / Draping API router
```

---

## 3. NGUYÊN TẮC PHÁT TRIỂN & VIẾT CODE

### 3.1. TypeScript & React Standards
- **Zero Build Errors:** Mọi pull request / thay đổi code phải pass lệnh `npm run build` (`tsc && vite build`) với 0 lỗi cảnh báo kiểu dữ liệu.
- **Strict Typing:** Không sử dụng kiểu `any` trừ trường hợp bắt buộc đối với WebGL raw buffers. Luôn định nghĩa interface rõ ràng trong `types.ts` hoặc data files.
- **Component Decomposition:** Không viết component vượt quá 400 dòng code. Khi logic hoặc UI phình to, tách thành sub-components (ví dụ: `BodyMorphingPanel`, `CompareModal`, `HistoryStatsBar`).

### 3.2. Three.js & 3D WebGL Guidelines
- **GLTFLoader Standards:** Sử dụng `import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'`.
- **Normalization:** Mọi mô hình `.glb` khi nạp vào Three.js phải được tính toán `Box3` để căn giữa tọa độ gốc (origin) và chuẩn hóa chiều cao (scale factor ~ 1.95 units).
- **Graceful Fallback:** Luôn giữ `procedural mannequin` (hình nộm hình học) làm phương án dự phòng ngay lập tức. Chỉ gỡ bỏ procedural mannequin khi sự kiện `GLTFLoader.onLoad` hoàn tất thành công.
- **Memory Safety:** Luôn dọn dẹp listeners (`window.removeEventListener`), hủy animation frame (`cancelAnimationFrame`), và gọi `renderer.dispose()` trong cleanup return của `useEffect`.

### 3.3. Design System & CSS Tokens
- Giao diện tuân thủ phong cách **Haute Couture Luxury Fashion Tech**:
  - Tông màu chủ đạo: Xanh hoàng gia sẫm (`#080a61`), xanh điểm nhấn (`#3d7eff`), nền kem ngà sang trọng (`#fbf8ff`), viền ánh kim và kính mờ (glassmorphism).
  - Không hardcode mã màu lung tung trong inline style. Sử dụng biến CSS token trong `:root` (ví dụ: `var(--vfit-primary)`, `var(--vfit-surface-card)`).

---

## 4. CHIẾN LƯỢC KẾT HỢP FRONTEND + BLENDER BODY

Khi người dùng thao tác thay đổi số đo hoặc chọn preset trong `UploadStep`:

1. **Preset Mode:** Người dùng chọn 1 trong 4 vóc dáng chuẩn (`Linh Đan`, `Minh Quân`, `Mai Anh`, `Thanh Trúc`). Hệ thống gán trực tiếp URL `.glb` tương ứng từ `frontend/public/models/`.
2. **Custom MPFB Sliders:** Người dùng kéo thanh trượt vai, eo, hông, ngực, cơ bắp, tone da:
   - Hệ thống đóng gói `BodyCustomParams`.
   - `tryonApi.generateBodyWithBlender(params)` gửi yêu cầu đến `http://localhost:8000/api/generate`.
   - Nếu Blender server phản hồi: Polling `job_id` cho đến khi hoàn tất -> nhận URL `.glb` mới tạo.
   - Nếu Blender server không hoạt động (offline / demo Vercel): Tự động gán model preset gần nhất và tính toán bảng số đo động để trải nghiệm không bị đứt đoạn.

---

## 5. QUY TRÌNH GIT VÀ QUẢN LÝ NHÁNH

1. **Nhánh chính:**
   - `main`: Nhánh production ổn định để deploy Vercel.
   - `origin/feature/*`: Nhánh tính năng cụ thể.
2. **Quy tắc đồng bộ:**
   - Trước khi code tính năng mới, luôn chạy: `git fetch origin` và kiểm tra trạng thái các nhánh.
   - Khi cần kết hợp code từ nhánh khác (như `feature/body` vào `feature/frontend-*`), sử dụng `git pull origin <branch_name>` và giải quyết triệt để xung đột.
   - Commit message chuẩn: `feat:`, `fix:`, `refactor:`, `docs:`.
3. **Cấu hình Vercel Deploy:**
   - Trong `vercel.json`, `buildCommand` trỏ tới `cd frontend && npm install && npm run build`.
   - `outputDirectory` là `frontend/dist`.
   - `rewrites` trỏ `/(.*)` về `/index.html` để chống lỗi 404 khi người dùng refresh hoặc truy cập trực tiếp route con.
