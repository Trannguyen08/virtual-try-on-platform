# Change Impact Log — chẩn đoán thời gian dựng cảnh thử đồ

- Thời gian: 2026-10-21 21:20:52 Asia/Saigon
- Vai trò thực hiện: M3 (worker); owner liên quan: M2 (Blender composition), M5 (trạng thái UI).
- Mục đích: giảm chi phí khởi động Blender không cần thiết và hiển thị đúng giai đoạn xử lý của image try-on.

## File thay đổi (trước → sau)

- `backend/workers/image_tryon.py`: lệnh `_compose` khởi động Blender với user startup và không đặt `--python-exit-code` → dùng `--factory-startup --python-exit-code 1`; `run_once` và `_process` chưa ghi thời gian từng giai đoạn → ghi thời gian chuẩn bị input, tái dựng áo, ghép cảnh Blender và tổng thời gian attempt. Không log ảnh, đường dẫn ảnh hoặc thông tin bí mật.
- `frontend/src/pages/tryon/ImageTryOnPage.tsx`: mọi job `running` đều ghi “Blender đang dựng cảnh thử đồ…” dù còn tái dựng ảnh → ghi “Đang tái dựng trang phục và ghép cảnh 3D…”.
- `.agents/memory/ACTIVE_CONTEXT.md` (local, Git ignore): thêm chẩn đoán job và thay đổi hiện tại.
- `docs/change-logs/20261021_212052_M3_blender_composition_startup.md`: chưa tồn tại → log này.

## Căn cứ và ảnh hưởng

- Job `itry_c381d2eeff744bd992d532875e7d92c6` đã hoàn tất, DB ghi từ 14:13:16 đến 14:14:26 UTC (khoảng 69 giây). Dấu thời gian file cho thấy input → normalized khoảng 3 giây, normalized → GLB áo khoảng 21 giây, metadata áo → scene GLB khoảng 44 giây. Dấu thời gian file chỉ định vị khoảng chậm, chưa tách chính xác thời gian mở Blender khỏi thời gian scheduling/validation.
- Chạy lại đúng body/garment GLB này trong Blender 5.2.2: script Python được cProfile đo khoảng 1,55 giây; toàn tiến trình bình thường 3,45 giây; `--factory-startup` 2,73 giây. Chế độ factory bỏ khởi tạo addon MPFB không được composer sử dụng. Hai GLB normal/factory có SHA-256 giống nhau và cùng báo penetration fraction `0.023716`. Đây là phép đo khi máy đã ấm; chưa chứng minh cold start 44 giây sẽ giảm tương ứng.
- Không đổi API, schema, đơn vị m/cm, hệ trục Y-up/+Z forward, ngưỡng kiểm tra mesh hoặc thuật toán M2. Job vẫn có trạng thái `pending/running/completed/failed`; UI chỉ sửa mô tả trạng thái `running`. Output thử nghiệm nằm trong `data/outputs/` (Git ignore), không thay đổi asset người dùng trong `data/assets/`.
- Nguy cơ: `--factory-startup` bỏ user addon/preferences của Blender; composer hiện chỉ dùng glTF import/export chuẩn và BVH, đã chạy thành công trên asset thật. Môi trường Blender khác chưa kiểm tra. `--python-exit-code 1` khiến lỗi Python trả exit code thất bại rõ ràng hơn; worker vẫn quét mã lỗi và trả lỗi có cấu trúc.

## Xác minh và bàn giao

- Gọi `_compose` qua worker với cùng input: hoàn tất khoảng 3,22 giây, penetration fraction `0.023716`, GLB byte-identical với scene đã hoàn tất của job. Không chạy lại toàn job từ ảnh, pytest hoặc kiểm thử trình duyệt.
- Worker đang chạy cần restart để nạp cờ Blender và log mới. Sau khi tạo job mới, owner M3 đối chiếu các dòng `input preparation`, `garment reconstruction`, `Blender composition`, `attempt finished` để xác định nơi còn chậm. M5 kiểm tra nhãn trạng thái trên web; M2 kiểm tra chất lượng các loại áo khác nếu có chênh lệch.
- Bốn GLB profiling tạm và wrapper Python trong `data/outputs/` đã được xóa bằng đường dẫn literal cụ thể sau khi đối chiếu output; asset gốc trong `data/assets/` được giữ nguyên. Không commit/push trong đợt này.
