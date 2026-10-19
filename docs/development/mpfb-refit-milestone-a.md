# Mốc A — Quần áo MHCLO refit theo body MPFB

Trạng thái: đã viết phần tích hợp; chưa tải asset/chạy test hoặc Blender.
Chưa nghiệm thu chất lượng hình ảnh hoặc khả năng mặc được trên ba body thật.

## Phạm vi đợt này

- Body mới lưu `.blend` MPFB còn topology/helpers/shape keys, bên cạnh GLB.
- Chọn áo, quần hoặc cả bộ qua catalog cấu hình; MHCLO fit trước khi bake/mask/export.
- Giữ material gốc, dùng material GAMEENGINE của MPFB cho GLB.
- Catalog frontend đọc các sản phẩm đủ asset từ backend. Mẫu mock cũ vẫn có nhãn minh họa.
- Có kiểm tra asset, báo lỗi, receipt cài đặt và report mỗi kết quả refit.

Chưa làm trang quản trị upload/duyệt, size chart thật, cloth simulation, worker
queue bền vững, xác thực người dùng hoặc khôi phục body-builder job sau restart.
M là nhãn thử nghiệm cho body-refit, không phải size đã đo của nhà sản xuất.

## 1. Cài hai pack mẫu (người dùng chạy)

Từ thư mục gốc dự án, dùng venv đã cài dependency backend:

```powershell
.\.venv\Scripts\python.exe -m garment.mpfb.setup --download-demo
```

Lệnh tải từ link mirror ZIP trên trang chính thức, không tải weights/AI:

- [shirts01](https://static.makehumancommunity.org/assets/assetpacks/shirts01.html),
  khoảng 23 MB; chọn `toigo_basic_tucked_t-shirt`, CC0, tác giả MargaretToigo.
- [pants01](https://static.makehumancommunity.org/assets/assetpacks/pants01.html),
  khoảng 20 MB; chọn `cortu_cargo_pants`, CC0, tác giả Cortu.

Giới hạn mỗi ZIP 64 MiB, giải nén 256 MiB; loại đường dẫn thoát root,
symlink và file thực thi. Asset đặt trong `data/external/mpfb/`, đã được
gitignore. Receipt lưu URL và SHA-256 pack/từng file. Chạy lại không ghi đè
file khác nội dung để giữ chỉnh sửa của người vận hành.

Nếu tải tự động không được, tải hai ZIP từ các trang trên rồi chạy:

```powershell
.\.venv\Scripts\python.exe -m garment.mpfb.setup --shirts-zip "C:/Downloads/shirts01.zip" --pants-zip "C:/Downloads/pants01.zip"
```

Thay tên/đường dẫn bằng file ZIP thực tế, không đổi cấu trúc bên trong pack.
Không bắt buộc cài pack vào thư mục MPFB của Blender; adapter đọc kho dự án.

Kiểm tra:

```powershell
.\.venv\Scripts\python.exe -m garment.mpfb.setup --check
```

Kỳ vọng ba ID `mpfb-tshirt`, `mpfb-pants`, `mpfb-outfit` đều SẴN SÀNG.
Nếu không khớp tên thư mục asset thực tế, chỉnh `assets` trong catalog theo
basename file hoặc thư mục chứa MHCLO. Không tự chọn ngẫu nhiên một asset.

## 2. Chạy và xem thử

Khởi động database/backend/frontend theo `run-backend-frontend.md`. Backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --env-file .env --reload --host 127.0.0.1 --port 8000
```

Frontend ở terminal khác:

```powershell
cd frontend
npm.cmd run dev
```

Reload trang Catalog hoặc bước chọn trang phục sau khi cài asset. Tìm
`Áo thun MPFB`, `Quần cargo MPFB` hoặc `Bộ áo thun và quần cargo MPFB`.
Ảnh catalog là biểu tượng, chưa phải thumbnail render asset. Chọn M rồi
tạo body mới; body GLB cũ không có `.blend` cần tạo lại. Viewer mở lớp Có
trang phục khi đã có job áo thành công. Swatch bị khóa để giữ material gốc.

API kiểm tra kho: `GET /api/body-builder/garments`, xem qua `/docs`.
`available=true` chỉ xác nhận dependency tồn tại/đọc được, chưa chứng minh
topology, material hoặc hình dáng đã qua kiểm tra Blender.

## 3. Quyền kiểm soát và thêm quần áo

Cấu hình mặc định: `garment/mpfb/catalog.json`. Không cần sửa code để thêm
một sản phẩm MHCLO tương thích:

1. Đặt toàn bộ MHCLO, OBJ, MHMAT, texture liên quan vào một thư mục trong
   `data/external/mpfb/`; giữ nguyên các tham chiếu tương đối.
2. Thêm entry theo mẫu dưới. Tên trong `assets` khớp stem MHCLO hoặc tên
   thư mục cha. Không giữ hai phiên bản cùng tên trong kho đang sử dụng.
3. Chạy `setup --check`, mở lại Catalog, thử ba body rồi mới dùng cho demo.

```json
{
  "id": "my-shirt",
  "name": "Áo của tôi",
  "category": "t_shirt",
  "gender": "menswear",
  "sizes": ["M"],
  "assets": ["my_shirt"],
  "license": "giấy phép của asset",
  "source": "nguồn hoặc tác giả của asset"
}
```

Một entry có nhiều `assets` tạo một bộ đồ. Kết quả giữ thứ tự nạp trong
danh sách; layering/va chạm giữa các món vẫn cần kiểm tra trực quan.
GLB/OBJ trần chưa có mapping cần chuẩn bị bằng MakeClothes; không tự trở
thành MHCLO chỉ vì đổi phần mở rộng.

Có thể đặt trong `.env` để dùng kho/catalog riêng:

```dotenv
MPFB_ASSET_ROOT=./data/external/mpfb
MPFB_GARMENT_CATALOG=./garment/mpfb/catalog.json
```

CLI setup không tự đọc `.env`. Nếu dùng đường dẫn riêng, truyền cùng cấu hình:

```powershell
.\.venv\Scripts\python.exe -m garment.mpfb.setup --asset-root "D:/MyGarments" --catalog "D:/MyGarments/catalog.json" --check
```

Backend nạp `.env` qua `--env-file`; đổi biến môi trường cần restart. Chỉnh
entry catalog/file asset chỉ cần reload giao diện và tạo job mới.

## 4. Kiểm thử nhẹ trước khi chạy Blender

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/garment/test_mpfb_catalog.py tests/unit/garment/test_mpfb_setup.py tests/unit/garment/test_mpfb_mapping.py tests/unit/backend/test_mpfb_refit_jobs.py tests/unit/backend/test_blender_job_errors.py -q
```

Kiểm tra TypeScript và build UI:

```powershell
cd frontend
npm.cmd run build
```

Tests dùng fixture và subprocess giả lập; không phải bằng chứng native refit thật.

## 5. Ma trận kiểm tra thật (người dùng chạy, có thể mất vài phút)

Sau khi backend chạy và asset đủ:

```powershell
.\.venv\Scripts\python.exe -m garment.mpfb.smoke
```

Tạo ba body tổng hợp nam cùng chiều cao 170 cm: gầy, trung bình, đầy đặn;
mỗi body thử áo, quần và cả bộ. Ghi report + chín GLB trong
`data/outputs/mpfb-validation/<thời_gian_UTC7>/`. Lệnh chạy tuần tự và dừng
khi lỗi; không gọi ảnh minh họa/method mock là refit thành công.

Kiểm tra tự động: job thành công, method/source đúng, GLB header/version/length
hợp lệ. **Chưa kiểm tra mesh bên trong GLB, nếp vải hay độ đẹp bằng mắt.**
Mở GLB trong Blender hoặc xem job tương ứng trên web, chụp trước/sau/hai bên:

- Form cổ/vai/tay, eo/hông/đũng quần không có lỗi rõ rệt.
- Vật liệu và texture giữ được trong web; không dùng áo một màu để che lỗi.
- Body và đồ cùng tỷ lệ/gốc; thay body khiến đồ biến dạng theo body.
- Không mất phần skin cần nhìn thấy do occlusion mask.
- Cả bộ không xuyên chồng rõ; chấp nhận/chỉnh lại asset theo từng trường hợp.

Sau đó thử thêm body nữ và chiều cao 150/195 cm trước khi công bố hỗ trợ
những nhóm đó. Chưa gắn nhãn unisex tương thích đã nghiệm thu cho asset nam.

## 6. Artifact và giới hạn vận hành

`data/outputs/blender_body/` chứa:

- `<body_job_id>.blend`: body MPFB trước bake/apply mask; không phục vụ qua URL public.
- `<body_job_id>.glb`: body hiển thị.
- `<clothing_job_id>.glb`: cảnh body + đồ đã refit, GLB Y-up, mét.
- `<clothing_job_id>.refit.json`: body parameters, phiên bản Blender/MPFB,
  hash catalog/adapter/MHCLO/mesh/material/texture; `cloth_simulation=false`,
  `fit_score=null`, `size_chart_verified=false`.

MHCLO có thể dùng occlusion mask để ẩn da dưới đồ. Đây không phải kiểm tra
collision hay bằng chứng áo thực sự vừa. Đợt này không scale size toàn bộ
asset để giả lập độ vừa; M chỉ là nhãn của cấu hình mẫu.

Job body-builder vẫn trong RAM: restart mất ID; cần tạo body mới. File trên
disk không tự biến thành job sau restart. Không xóa `.blend` nếu còn cần
thay trang phục trên body hiện tại. Khi nâng Blender/MPFB phải tạo body mới
để tránh dùng scene khác phiên bản.

## 7. Các mốc tiếp theo

A chỉ được đánh dấu nghiệm thu sau khi chạy matrix và kiểm tra ảnh thật.
Sau đó B: quản lý body/garment/job bền vững, contract và worker; C: trang
quản trị upload/duyệt/version asset; D: vận hành; E: size thật và cloth.
Không coi việc có catalog JSON là đã hoàn thành trang quản trị hay production.
