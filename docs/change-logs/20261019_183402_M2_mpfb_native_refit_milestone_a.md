# Mốc A — Native MPFB refit, catalog cấu hình và bộ kiểm tra

Thời điểm: 2026-10-19 18:34:02 UTC+7 (Asia/Saigon).
Vai trò chính M2, tích hợp M1/M3/M5 theo phê duyệt kế hoạch của user.

## Mục đích và hiện trạng

User duyệt hướng kho quần áo MHCLO + MPFB refit, yêu cầu làm thử và ghi log.
Đợt này triển khai phần mềm của mốc A; chưa tuyên bố nghiệm thu mốc A.
Đã đọc bản MPFB cài trên máy: manifest 2.0.6 trong cây Blender 5.2;
đối chiếu trực tiếp HumanService.add_mhclo_asset, ClothesService,
Mhclo và TargetService. Không tìm thấy MHCLO trong kho MPFB mặc định
đã kiểm tra hoặc asset clothing của repo. Không suy ra mọi thư mục khác
trên máy đều không có asset; hỗ trợ cấu hình kho riêng.

## Từng file thực tế thêm/sửa, trước → sau

### M2 — mới

- `garment/mpfb/__init__.py`: package tích hợp, không import bpy khi nạp.
- `garment/mpfb/catalog.json`: ba mẫu `mpfb-tshirt`, `mpfb-pants`,
  `mpfb-outfit`, tham chiếu áo `toigo_basic_tucked_t-shirt` (shirts01)
  và quần `cortu_cargo_pants` (pants01), nguồn/giấy phép CC0 theo trang
  asset pack chính thức, sizes M và metadata menswear.
- `garment/mpfb/catalog.py`: validate catalog/choice; resolve asset duy nhất
  trong root; kiểm tra mesh/material/texture tham chiếu tồn tại trong kho;
  trạng thái available/error_code không trả đường dẫn disk. Availability
  chưa kiểm tra hình học, ảnh texture giải mã hoặc chất lượng Blender.
- `garment/mpfb/blender_fitting.py`: validate mapping/body indices,
  scale references/NaN/coverage; gọi API MPFB GAMEENGINE trước bake;
  parenting/local transform để chiều cao body áp dụng một lần; giới hạn
  mỗi garment <=30k vertex; giữ material gốc, không scale giả theo size;
  tạo report có thông số, versions, hashes, size/cloth/fit provenance.
- `garment/mpfb/setup.py`: CLI chỉ chạy khi user gọi; tải hai ZIP nhỏ từ
  mirror trên trang chính thức hoặc nhập ZIP cục bộ; kiểm tra path/link,
  kích thước, extension; không ghi đè file đã sửa; lưu receipt SHA-256.
  Không tải gì khi backend/import module.
- `garment/mpfb/smoke.py`: CLI user chạy ma trận API thật 3 body tổng hợp
  × 3 cấu hình trang phục; tuần tự, kiểm tra method/source và header GLB;
  lưu GLB/report trong data/outputs. Báo visual_quality_verified=false,
  không coi header hợp lệ là hình đẹp hoặc fit chính xác.

### M1 — sửa

- `body/estimation/blender_body.py`: trước body bake/apply MASK ngay,
  clothing chỉ import GLB nên mất topology/targets MPFB. Sau tách
  load_mpfb_services, mpfb_version, prepare_body_export; lấy bounds từ
  evaluated body có modifier; lưu `.blend` native trước bake/export cùng
  thông số/Blender/MPFB/generator hash. Nhánh catalog MHCLO mở scene native
  server-generated với use_scripts=False, kiểm tra version/tag/shape keys,
  gọi adapter refit rồi bake/mask để export. Ghi `.refit.json` sau GLB.
  Nhánh trang phục synthetic/GLB cũ vẫn tồn tại cho ID ngoài catalog MHCLO.

### M3 — sửa

- `backend/services/blender_body.py`: trước không kiểm tra native scene,
  chưa biết method refit. Sau preflight category/size/dependencies/native
  scene, body completion cần `.blend`, native refit completion cần report
  hợp lệ; thêm method blender_mpfb_refit/source module hoặc mixed. Giữ job
  store RAM, timeout/concurrency hiện hữu và xử lý failed có cấu trúc.
- `backend/api/body_builder.py`: thêm GET `/api/body-builder/garments`
  theo SuccessResponse. Request clothing và các route cũ không đổi.
- `.env.example`: thêm MPFB_ASSET_ROOT/MPFB_GARMENT_CATALOG với mặc định
  trong repo. Không sửa `.env` của user, dependency hoặc môi trường.

### M5 — sửa/thêm

- `frontend/src/api/bodyBuilderApi.ts`: thêm type RefitGarment và client
  garments(); không đổi wire job hiện hữu.
- `frontend/src/data/mockProducts.ts`: thêm optional fittingMode.
- `frontend/src/hooks/useGarmentProducts.ts`: mới; lấy catalog backend,
  chỉ đưa mẫu đủ dependency vào chọn đồ; giữ mẫu cũ, báo trạng thái thiếu
  asset/backend; map metadata sang Product. Chỉnh config rồi reload trang
  có thể thêm mẫu MHCLO mới mà không sửa code frontend.
- `frontend/src/pages/catalog/CatalogPage.tsx`: dùng hook thay danh sách
  chỉ mock; category Quần, count/filter phụ thuộc products; status kho.
- `frontend/src/components/tryon/SelectGarmentStep.tsx`: danh sách động,
  status kho và giải thích body-refit/M chưa là size thật.
- `frontend/src/pages/tryon/TryOnPage.tsx`: progress text theo mode.
- `frontend/src/components/tryon/GeneratedBodyViewer.tsx`: nhận diện
  method refit, giữ material/khóa swatch khi refit, provenance rõ;
  mở lớp Có trang phục khi có initial clothing job thành công.
- `frontend/public/images/mpfb-tshirt.svg`, `mpfb-pants.svg`: mới,
  biểu tượng catalog; chưa phải ảnh render asset thực tế.

### Kiểm thử/tài liệu — mới/sửa

- Mới `tests/unit/garment/test_mpfb_catalog.py`: TC-GAR-02 cho dependency,
  asset mất texture, escape path, duplicate version, catalog sai và size.
- Mới `tests/unit/garment/test_mpfb_setup.py`: TC-GAR-02 cho import ZIP
  idempotent, giữ sửa local, kiểm tra đường dẫn trước ghi, chọn mirror.
- Mới `tests/unit/garment/test_mpfb_mapping.py`: TC-GAR-02 cho index/
  coverage/scaling/NaN; không phụ thuộc bpy.
- Mới `tests/unit/backend/test_mpfb_refit_jobs.py`: TC-API-03 với Blender
  giả lập, native body/refit report/provenance, legacy body, thiếu artifact,
  catalog status. Fixture file không phải `.blend`/GLB thật đã nghiệm thu.
- Mới `docs/development/mpfb-refit-milestone-a.md`: lệnh cài/check/run,
  thêm sản phẩm, cấu hình, kiểm tra nhẹ và acceptance matrix, giới hạn.
- Sửa `docs/api/api-contract.md`: phụ lục body-builder native refit,
  method/error codes/catalog endpoint và giới hạn. Không đổi `/api/tryon`.
- Thêm chính file log này, không sửa log cũ.

## API/schema, đơn vị, database, asset

- API thêm một GET và một giá trị method. Các field request/job/envelope
  cũ giữ nguyên; consumer viewer đã cập nhật theo method mới.
- Internal Blender adapter dùng mét/Z-up với native MakeHuman topology;
  exporter Y-up giữ nguyên. World transform body kế thừa một lần qua
  parenting, không căn giữa body/garment riêng. +Z forward cần kiểm chứng
  trong acceptance hình ảnh, chưa có render xác nhận cho asset mới.
- Database không thay đổi; body-builder job vẫn trong RAM. Restart mất
  ID; native scene/report trên disk không có cơ chế tự khôi phục job.
- Asset/ZIP/receipt/native `.blend`/report/GLB được tạo khi user chạy,
  nằm trong data/external hoặc data/outputs đã gitignore. Đợt agent này
  không tải asset, tạo binary lớn, dataset hay weights. Không đổi package.
- Size M chỉ là nhãn thử nghiệm. Không có chart nhà sản xuất, metric
  fit/score hay cloth simulation; source module mô tả nguồn xử lý.

## Xung đột/nguy cơ đã biết, owner phối hợp

- Đã xác nhận: GLB cũ không đủ topology/shape keys cho MHCLO refit; chặn
  bằng BODY_REFIT_DATA_MISSING và yêu cầu tạo body mới.
- Đã xác nhận: MPFB có nhánh bỏ qua index body không tồn tại trong fitting;
  adapter kiểm tra trước để không coi kết quả sai topology là thành công.
- MHCLO có thể mask da dưới quần áo; report ghi body_occlusion_masks=true.
  Mask không chứng minh không xuyên mesh hoặc size thực sự vừa.
- Chưa kiểm tra: native roundtrip trên Blender 5.2/MPFB 2.0.6 thật, material
  GAMEENGINE export, form áo/quần và layering trên các body trong matrix.
- Tên thư mục/stem trong pack chưa kiểm tra qua ZIP thực tế; setup --check
  sẽ báo thiếu hoặc ambiguous, không âm thầm chọn asset khác. Có thể cần
  chỉnh `assets` theo kho user dùng.
- Download mirror có thể đổi hoặc không truy cập được; hỗ trợ ZIP offline.
  Cài pack có lỗi giữa chừng có thể để lại file đã ghi; rerun cùng pack
  idempotent, không rollback đè/xóa asset user sửa.
- Catalog là file operator quản lý, chưa có upload/duyệt/auth/version UI.
  Không coi đây là production nhiều người dùng. Native `.blend` là file
  nội bộ do server tạo, không mở file `.blend` upload tùy ý qua API.
- M1: kiểm tra chiều cao/native body nhất quán; M2: validate asset, hình
  dáng/topology/material; M3: kiểm tra job/errors/artifacts; M5: build và
  kiểm tra catalog/viewer; M4: chưa sửa hoặc xác nhận fit metrics.
- Nhánh đã đọc trước đó là feature/body; không chạy Git/đổi nhánh. Các
  thay đổi liên module cần review theo owner trước khi gộp nhánh.

## Kết quả kiểm thử thực tế

Chưa chạy test (Chờ User xác nhận). Chưa tải ZIP, chạy Blender, pytest,
TypeScript build, server hoặc Git. Chỉ đọc file, đối chiếu API MPFB cài
trên máy, viết/rà soát patch và tài liệu. Không có bằng chứng PASS hoặc
ảnh render cho phần MHCLO mới; không đánh dấu mốc A hoàn tất nghiệm thu.

Lệnh kiểm tra và hướng dẫn đầy đủ nằm trong tài liệu mốc A. Bước đầu:

```powershell
.\.venv\Scripts\python.exe -m garment.mpfb.setup --download-demo
.\.venv\Scripts\python.exe -m garment.mpfb.setup --check
```

Sau khi backend chạy và asset đủ, ma trận thực tế:

```powershell
.\.venv\Scripts\python.exe -m garment.mpfb.smoke
```

## Bàn giao và phần còn lại

User chạy kiểm tra nhẹ/build/cài asset, tạo body mới và chọn bộ MPFB;
chạy matrix, lưu report + ảnh trước/sau/hai bên. Sửa lỗi native/material
theo log thật trước khi nghiệm thu. Sau đó mới tiếp tục mốc B (persist
job/body/catalog + worker), C (admin workflow), D (vận hành), E (size thật
và cloth). Không mở rộng thêm AI dựng đồ từ ảnh trong đợt này.
