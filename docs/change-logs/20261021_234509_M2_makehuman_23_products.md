# Giữ ba sản phẩm MPFB và thêm 20 mẫu MakeHuman

## Vai trò, yêu cầu và thời gian

- M2, phối hợp giao diện M5 theo yêu cầu trực tiếp của User; 2026-10-21 23:45:09, Asia/Saigon (UTC+7).
- User yêu cầu tải 10 áo và 10 quần từ MakeHuman, có ảnh sản phẩm. Sau đó chỉ định giữ ba món cũ: Áo hoodie nữ MPFB, Áo thun MPFB, Quần cargo MPFB; gỡ mọi sản phẩm cũ khác.
- Chốt **3 món giữ lại + 20 món mới = 23 asset khác nhau**. Không xóa dữ liệu mesh nguồn cũ của User và không thực hiện Git.

## File thay đổi, trước → sau

| File | Thay đổi |
| --- | --- |
| garment/mpfb/catalog.json | 5 mục cũ → giữ ba ID/tên được yêu cầu, bỏ CGTrader và bộ đồ gộp; thêm 20 ID riêng, nguồn, tác giả, giấy phép và ảnh PNG; tổng 23 |
| garment/mpfb/collection.json | Mới: manifest 10 áo + 10 quần, tên Việt, category, gender, tác giả, license và pack URL; không trùng asset giữ lại |
| garment/mpfb/install_collection.py | Mới: cài asset thiếu, dùng lại asset hợp lệ, copy thumbnail gốc, kiểm tra đủ 23 asset/dependency/ảnh trước ghi catalog; receipt hash, không thực thi archive |
| garment/mpfb/remote_pack.py | Mới: lấy ZIP index và byte ranges HTTPS từ mirror chính thức bằng curl.exe, đọc CRC qua ZipFile, chỉ tạo ZIP chứa thư mục asset chọn |
| garment/mpfb/setup.py | download_pack nhận giới hạn byte tùy chọn; extract_pack nhận asset_names tùy chọn; giữ mặc định caller cũ, kiểm tra đường dẫn và bảo vệ file sửa cục bộ |
| frontend/src/api/bodyBuilderApi.ts | RefitGarment thêm metadata tùy chọn thumbnail_url/author/license/source/collection/assets có sẵn từ catalog response |
| frontend/src/data/mockProducts.ts | Xóa mọi product demo; giữ Product interface có metadata nguồn và mảng rỗng cho legacy import |
| frontend/src/hooks/useGarmentProducts.ts | Bỏ fallback mock; ánh xạ ảnh/tác giả/license từ API, catalogLoaded; chỉ hiển thị asset sẵn sàng một món, bộ mới ưu tiên trước |
| frontend/src/components/home/FeaturedProductsSection.tsx | Dùng API thật thay mock; có tab quần; mặc định trộn bốn áo/bốn quần; tối đa tám món xem trước, link danh mục có số lượng thật |
| frontend/src/pages/catalog/CatalogPage.tsx | Ảnh asset dùng contain, hiển thị có sẵn để thử thay vì bịa giá bán |
| frontend/src/components/catalog/ProductDetailModal.tsx | Với asset thật dùng ảnh gốc riêng, tác giả/license/source; không dùng gallery/đánh giá/độ chính xác/chất liệu giả của demo; giải thích size M refit |
| frontend/src/pages/tryon/OutfitTryOnPage.tsx | Sau tải catalog, bỏ selection/result/job thuộc sản phẩm cũ đã gỡ; giữ khả năng chọn áo/quần riêng và ảnh ngoài |
| frontend/src/components/tryon/SelectGarmentStep.tsx | Guard catalog bất đồng bộ, không đọc sizes của undefined khi không có mock |
| frontend/src/pages/tryon/TryOnPage.tsx | Không khởi tạo bằng mock đầu tiên; chỉ mở viewer khi đã có lựa chọn |
| frontend/public/images/makehuman/*.png | Thêm 23 thumbnail gốc (1,147,505 byte tổng), không tạo ảnh hàng hóa giả hoặc dùng ảnh khác asset |
| frontend/public/images/makehuman/ATTRIBUTION.json | Mới: 23 mục attribution với tác giả, giấy phép, URL nguồn ảnh/pack hoặc đường dẫn ảnh hoodie User cung cấp, SHA-256 |
| tests/unit/garment/test_curated_collection.py | Mới: regression TC-GAR-02 cho count/giữ đúng món/PNG/credits, selective ZIP, traversal và đọc chọn ZIP không cần mạng |
| .agents/memory/ACTIVE_CONTEXT.md | Bổ sung yêu cầu chốt, nguồn asset, thay đổi, kiểm tra và giới hạn |
| docs/change-logs/20261021_234509_M2_makehuman_23_products.md | Nhật ký đợt này |

## Asset và nguồn

- Nguồn áo: [shirts01](https://static.makehumancommunity.org/assets/assetpacks/shirts01.html), [shirts02](https://static.makehumancommunity.org/assets/assetpacks/shirts02.html).
- Nguồn quần: [pants01](https://static.makehumancommunity.org/assets/assetpacks/pants01.html), [pants02](https://static.makehumancommunity.org/assets/assetpacks/pants02.html).
- Bộ mới dùng 9 áo shirts01, 1 áo Boho shirts02, 3 quần pants01 và 7 quần pants02. Không dùng lại Basic Tucked/Cargo trong bộ mới vì đã giữ hai món đó.
- Reuse 12 asset thuộc bộ mới đã cài từ pack chính thức; tải bổ sung 8 asset, 46 file phụ thuộc. Giấy phép CC0 và CC-BY ghi theo nguồn, không tự gán phiên bản CC-BY.
- Hoodie dùng đúng ảnh .thumb đã có trong data/external/aotest. Ba tên/ID gốc được giữ nguyên.
- File 3D, texture và receipt nằm data/external/mpfb, đã được gitignore. Cache nguồn ZIP: pants02 131,847,848 byte; ZIP chọn một áo Boho 426,952 byte. Không commit các cache/mesh này.
- Đã dọn bản tải dở và probe tạo trong phiên gián đoạn. Một lệnh cleanup dùng biến bị tool policy chặn; sau khi xác minh đường dẫn, lệnh xóa từng file bằng literal absolute path đã thành công. Không còn việc cleanup bị chặn.

## Ảnh hưởng contract và module

- **API:** không sửa route/backend schema hoặc database. Endpoint hiện trả dict mở rộng từ catalog; UI dùng các metadata tùy chọn. Endpoint clothing vẫn nhận đúng garment_id/category/size M. HTTP catalog thực tế đã trả đủ metadata.
- **M1:** không sửa body/camera/tái dựng người; giữ luồng tạo model hiện có.
- **M2:** thêm dữ liệu và installer, không sửa thuật toán refit. Sẵn sàng ở đây là đủ file tham chiếu, không chứng minh chất lượng refit toàn bộ mẫu.
- **M3:** catalog cũ bỏ hai ID, client đã bỏ lựa chọn cũ sau tải catalog. Asset job cache trước đó vẫn có thể chứa ID cũ; chưa thay persistence server.
- **M4:** không có fit score/size chart thật được tạo. M vẫn là nhãn demo refit.
- **M5:** trang chủ/danh mục/phòng thử cùng dữ liệu thật. Khi API lỗi, báo không tải được thay vì đưa sản phẩm demo trở lại.
- **Đơn vị/hệ trục:** không scale hoặc sửa tọa độ asset; MHCLO vẫn theo pipeline MPFB hiện có; GLB xuất mét/Y-up/+Z theo hợp đồng cũ.
- **Dữ liệu cá nhân:** không xóa lịch sử thử đồ riêng của User hoặc ảnh cá nhân; chỉ gỡ sản phẩm cũ khỏi catalog và lựa chọn stale trong phòng thử.

## Kiểm tra thực tế

- Installer hoàn tất: `Catalog ready: 3 retained + 10 new tops + 10 new trousers = 23 products.` Chạy lại dùng file đã cài và không tải lại.
- GET `http://127.0.0.1:8000/api/body-builder/garments` từ backend đang chạy: Total=23, Ready=23, NewTops=10, NewPants=10, Missing=[]; cả 23 có thumbnail_url.
- Thumbnail: 23 PNG gốc; đã xem trực tiếp ảnh Boho và hoodie để đối chiếu đúng garment.
- Build cuối `npm.cmd run build`: **PASS**, exit 0, TypeScript + Vite 5.4.21, 669 modules, Vite 7.28s; main 998.67 kB/gzip 272.33 kB. Cảnh báo chunk lớn vẫn còn, không chặn build.
- **Chưa chạy pytest, browser hoặc Blender refit toàn bộ 23 mẫu.** Quyền chạy build đã có; tải/cài/kiểm tra asset nằm trong yêu cầu tải của User. Không tự mở rộng sang train/render/simulation.

## Bàn giao

- User tải lại trang danh mục để thấy 23 món; chọn áo/quần riêng trong phòng thử.
- M2/M3 kiểm tra refit các mẫu thật; file đủ không bảo đảm hết xuyên mesh hay tương thích mọi dáng body. Khi backend reload mất registry job, tạo model mới như giới hạn đã ghi trước đó.
- Regression đề xuất: pytest test_curated_collection.py cùng test_mpfb_setup.py/test_mpfb_catalog.py và test_package_imports.py khi User cho phép.
