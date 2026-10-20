# Change Impact Log — đăng ký aotest hoodie

- Thời điểm: 2026-10-19 20:17:23 Asia/Saigon.
- Vai trò M2; dùng m2-garment-expert và change-impact-log.
- Mục đích: đưa mẫu người dùng đặt trong data/external/aotest vào catalog MPFB hiện có.

## File và thay đổi

| File | Trước → sau |
|---|---|
| `data/external/aotest/ladieshoodiedown1.mhclo.txt` | Chuyển sang `data/external/mpfb/aotest/ladieshoodiedown1.mhclo`, bỏ đuôi .txt, giữ mapping MakeClothes. |
| `data/external/aotest/ladieshoodiedown1.mhmat.txt` | Chuyển sang `data/external/mpfb/aotest/ladieshoodiedown1.mhmat`, bỏ đuôi .txt, giữ material và texture references. |
| `data/external/mpfb/aotest/IMPORT-NOTES.md` | File mới: nguồn, attribution Elvaerwyn/CC_by chưa rõ version, file còn thiếu, cách hoàn thiện và giới hạn. |
| `garment/mpfb/catalog.json` | Thêm `mpfb-aotest-hoodie`, jacket/womenswear/M, engine mhclo, asset ladieshoodiedown1, metadata nguồn từ header. |
| File log này | File mới ghi lại thay đổi và bàn giao. |

Thumbnail gốc giữ nguyên tại data/external/aotest; không sửa/giả lập mesh hoặc texture.

## Ảnh hưởng

- API/schema: không sửa cấu trúc; catalog có thêm một entry. `resolve_assets` và
  `asset_dependencies` hiện có kiểm tra file tham chiếu; entry sẽ unavailable vì thiếu mesh/texture.
  Hook frontend hiện có chỉ hiển thị mẫu available. Chưa xác minh qua HTTP runtime.
- Asset: MHCLO chỉ định hm08, `ladieshoodiedown1.obj`, material tương ứng;
  material chỉ định `hoodietex1.png`, `normalshoodie.png`. Cả ba file này chưa có trong thư mục upload.
- Không đổi đơn vị, hệ trục, API contract, database hay code fitting.
  Chưa kiểm tra geometry/đơn vị/trọng số xương vì không có mesh nguồn.
- Owner phối hợp: M2 nhận đủ asset và thử refit; M3/M5 xác nhận catalog availability và hiển thị.
- Kích thước asset hiện có dưới 50MB, nằm trong data/external là vùng tài nguyên không commit.

## Xung đột và rủi ro

- Đã xác nhận thiếu dependency; không thể tuyên bố mặc thử được.
- MHCLO thuộc hoodie nữ, không phải quần Harem hoặc áo GLTF trước đây.
- Không thay mesh khác vào mapping này để tránh sai vertex indices.
- Nhánh đọc từ .git/HEAD là feature/body, khác nhánh M2 khuyến nghị feature/garment;
  chỉ sửa catalog và asset theo yêu cầu người dùng, không chuyển nhánh hoặc chạy Git.
  Chưa kiểm tra xung đột merge.
- Giấy phép header CC_by chưa ghi version; giữ attribution, cần kiểm tra trang gốc trước phân phối.

## Kiểm chứng và bàn giao

Đã đọc header MHCLO, material và thư mục upload; kiểm tra lại các file đích và entry bằng đọc file.
Chưa chạy test, Blender, frontend hoặc backend; chưa có kết quả refit/render/animation.
Không thêm test riêng cho thay đổi catalog đơn giản; dùng dependency checks sẵn có.
Người dùng cần đặt đúng ba file thiếu vào data/external/mpfb/aotest, sau đó refresh catalog,
chọn Áo hoodie nữ MPFB — aotest, size M, tạo body nữ mới và gửi ảnh/log nếu có lỗi.
Nếu cấu hình MPFB_ASSET_ROOT hoặc MPFB_GARMENT_CATALOG tùy chỉnh, cần dùng đúng root/catalog đó;
không tìm thấy các khóa cấu hình này qua lần đọc chọn lọc trong .env.
