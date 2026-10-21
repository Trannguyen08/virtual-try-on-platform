# Change Impact Log: tích hợp body, garment và fit

- Thời điểm: 2026-10-19 20:30:24 (Asia/Saigon).
- Vai trò: M3 điều phối tích hợp; ảnh hưởng M2, M4, M5 và hạ tầng chung.
- Mục đích: tạo nhánh `integration/tryon-body-garment-fit` từ `db8bade`, merge `origin/feature/clothes` tại `ad788df` thành `34125ad`, giữ thay đổi địa phương của người dùng, và đánh giá ba điểm tích hợp.
- Conflict Git: không có conflict nội dung. Merge ban đầu dừng vì `.gitignore` có thay đổi địa phương; đã cất riêng đúng file này, merge và áp lại nguyên dòng `data/assets/`. `LichSuCommit.txt` không bị sửa.

## Danh sách file trong merge commit

Bảng dưới ghi từng file theo diff `db8bade..34125ad`. `M` là file đã có ở nhánh gốc và nhận phiên bản từ merge; `A` là chưa có → được thêm; `D` là có → bị xóa trong merge commit. Các thay đổi nội dung quan trọng được diễn giải ngay sau bảng.

| Trạng thái | File | Trước → sau |
| --- | --- | --- |
| M | `.agents/rules/common/01_agent_behavior.md` | phiên bản db8bade → phiên bản sau merge |
| D | `.agents/rules/common/05_change_impact_log.md` | có tại db8bade → bị xóa trong merge commit |
| M | `.gitignore` | phiên bản db8bade → phiên bản sau merge |
| M | `AGENTS.md` | phiên bản db8bade → phiên bản sau merge |
| A | `ai/chatbot/__init__.py` | chưa tồn tại → được thêm từ nhánh clothes |
| A | `ai/chatbot/guardrails.py` | chưa tồn tại → được thêm từ nhánh clothes |
| A | `ai/chatbot/prompt_templates.py` | chưa tồn tại → được thêm từ nhánh clothes |
| A | `ai/chatbot/stylist_agent.py` | chưa tồn tại → được thêm từ nhánh clothes |
| M | `ai/models/__init__.py` | phiên bản db8bade → phiên bản sau merge |
| A | `ai/models/dynamic_size_advisor.py` | chưa tồn tại → được thêm từ nhánh clothes |
| M | `ai/models/size_recommender.py` | phiên bản db8bade → phiên bản sau merge |
| M | `backend/core/config.py` | phiên bản db8bade → phiên bản sau merge |
| M | `backend/db/session.py` | phiên bản db8bade → phiên bản sau merge |
| M | `backend/garment3d/.env.example` | phiên bản db8bade → phiên bản sau merge |
| M | `backend/garment3d/router.py` | phiên bản db8bade → phiên bản sau merge |
| M | `backend/garment3d/settings.py` | phiên bản db8bade → phiên bản sau merge |
| M | `backend/main.py` | phiên bản db8bade → phiên bản sau merge |
| A | `docs/M4_FIT_AI_MODULE.md` | chưa tồn tại → được thêm từ nhánh clothes |
| A | `docs/change-logs/20261019_160000_M2_guided_segmentation_prop_pruning_and_auto_garment_type.md` | chưa tồn tại → được thêm từ nhánh clothes |
| A | `docs/change-logs/20261019_174500_M2_modular_pipeline_hollow_hem_and_plain_back_texture.md` | chưa tồn tại → được thêm từ nhánh clothes |
| M | `docs/testing/test-cases/test-cases-fit-ai.md` | phiên bản db8bade → phiên bản sau merge |
| M | `fit/__init__.py` | phiên bản db8bade → phiên bản sau merge |
| A | `fit/diagnostics.py` | chưa tồn tại → được thêm từ nhánh clothes |
| A | `fit/evaluator.py` | chưa tồn tại → được thêm từ nhánh clothes |
| M | `fit/heatmap/heatmap_exporter.py` | phiên bản db8bade → phiên bản sau merge |
| M | `fit/heatmap/heatmap_generator.py` | phiên bản db8bade → phiên bản sau merge |
| M | `fit/metrics/coverage.py` | phiên bản db8bade → phiên bản sau merge |
| M | `fit/metrics/distance.py` | phiên bản db8bade → phiên bản sau merge |
| M | `fit/metrics/penetration.py` | phiên bản db8bade → phiên bản sau merge |
| M | `fit/region/body_regions.py` | phiên bản db8bade → phiên bản sau merge |
| M | `fit/region/region_fit.py` | phiên bản db8bade → phiên bản sau merge |
| M | `fit/score/classification.py` | phiên bản db8bade → phiên bản sau merge |
| M | `fit/score/fit_score.py` | phiên bản db8bade → phiên bản sau merge |
| A | `fit/utils/proximity.py` | chưa tồn tại → được thêm từ nhánh clothes |
| M | `frontend/src/api/garment3d.ts` | phiên bản db8bade → phiên bản sau merge |
| M | `frontend/src/components/GarmentImageInputs.tsx` | phiên bản db8bade → phiên bản sau merge |
| M | `frontend/src/pages/Garment3DPage.tsx` | phiên bản db8bade → phiên bản sau merge |
| M | `garment/__init__.py` | phiên bản db8bade → phiên bản sau merge |
| M | `garment/mesh/__init__.py` | phiên bản db8bade → phiên bản sau merge |
| M | `garment/mesh/mesh_generator.py` | phiên bản db8bade → phiên bản sau merge |
| A | `garment/mesh/pants_generator.py` | chưa tồn tại → được thêm từ nhánh clothes |
| M | `garment/mesh/size_scaling.py` | phiên bản db8bade → phiên bản sau merge |
| A | `garment/reconstruction/classifier.py` | chưa tồn tại → được thêm từ nhánh clothes |
| M | `garment/reconstruction/contracts.py` | phiên bản db8bade → phiên bản sau merge |
| A | `garment/reconstruction/landmarks.py` | chưa tồn tại → được thêm từ nhánh clothes |
| M | `garment/reconstruction/local_pipeline.py` | phiên bản db8bade → phiên bản sau merge |
| A | `garment/reconstruction/mesh_builder.py` | chưa tồn tại → được thêm từ nhánh clothes |
| A | `garment/reconstruction/segmentation.py` | chưa tồn tại → được thêm từ nhánh clothes |
| M | `garment/simulation/__init__.py` | phiên bản db8bade → phiên bản sau merge |
| A | `garment/simulation/blender/blender_cloth_sim.py` | chưa tồn tại → được thêm từ nhánh clothes |
| M | `garment/simulation/draping.py` | phiên bản db8bade → phiên bản sau merge |
| M | `garment/simulation/simulator.py` | phiên bản db8bade → phiên bản sau merge |
| M | `garment/size_chart/__init__.py` | phiên bản db8bade → phiên bản sau merge |
| M | `garment/size_chart/charts/pants.json` | phiên bản db8bade → phiên bản sau merge |
| M | `garment/size_chart/charts/shirt.json` | phiên bản db8bade → phiên bản sau merge |
| A | `garment/size_chart/charts/tshirt.json` | chưa tồn tại → được thêm từ nhánh clothes |
| M | `garment/size_chart/garment_loader.py` | phiên bản db8bade → phiên bản sau merge |
| A | `scripts/benchmark_empirical_evaluation.py` | chưa tồn tại → được thêm từ nhánh clothes |
| A | `scripts/demo_ai_chatbot_and_advisor.py` | chưa tồn tại → được thêm từ nhánh clothes |
| A | `scripts/demo_fit_evaluation.py` | chưa tồn tại → được thêm từ nhánh clothes |
| A | `scripts/test/test_real_garment_pipeline.py` | chưa tồn tại → được thêm từ nhánh clothes |
| M | `shared/constants/body_regions.py` | phiên bản db8bade → phiên bản sau merge |
| M | `shared/constants/units.py` | phiên bản db8bade → phiên bản sau merge |
| M | `shared/interfaces/fit.py` | phiên bản db8bade → phiên bản sau merge |
| M | `tests/unit/ai/test_ai.py` | phiên bản db8bade → phiên bản sau merge |
| A | `tests/unit/ai/test_chatbot.py` | chưa tồn tại → được thêm từ nhánh clothes |
| A | `tests/unit/ai/test_dynamic_size_advisor.py` | chưa tồn tại → được thêm từ nhánh clothes |
| M | `tests/unit/fit/test_fit.py` | phiên bản db8bade → phiên bản sau merge |
| A | `tests/unit/garment/__init__.py` | chưa tồn tại → được thêm từ nhánh clothes |
| M | `tests/unit/garment/reconstruction/test_local_pipeline.py` | phiên bản db8bade → phiên bản sau merge |
| M | `tests/unit/garment/test_garment.py` | phiên bản db8bade → phiên bản sau merge |
| A | `tests/unit/garment/test_pants.py` | chưa tồn tại → được thêm từ nhánh clothes |
| A | `tests/unit/garment/test_simulation.py` | chưa tồn tại → được thêm từ nhánh clothes |

## Chỉnh lý sau merge và thay đổi địa phương

- `AGENTS.md`: merge thêm yêu cầu đọc/cập nhật memory và giảm danh sách quy tắc chung từ 5 xuống 4; đã giữ yêu cầu memory, thêm hướng dẫn tạo file ở checkout mới và khôi phục mục Rule 05 theo chỉ thị người dùng.
- `.agents/rules/common/05_change_impact_log.md`: merge xóa file; đã khôi phục nội dung từ `db8bade` sau merge.
- `.agents/memory/ACTIVE_CONTEXT.md`: trước không tồn tại → đã tạo và ghi trạng thái nhánh, các phát hiện, giới hạn xác minh. File này được `.gitignore` loại trừ theo chủ ý của nhánh nguồn, nên chỉ lưu trên máy hiện tại.
- `.gitignore`: merge thêm quy tắc ignore memory; dòng `data/assets/` là thay đổi đã có của người dùng trước khi bắt đầu và vẫn là thay đổi chưa commit. `LichSuCommit.txt` vẫn untracked và nguyên trạng.

## Ảnh hưởng và xung đột có căn cứ

- **Database:** `backend/core/config.py:Settings.database_url` đổi mặc định PostgreSQL thành `sqlite+pysqlite:///./data/tryon.sqlite3`; `backend/db/session.py:make_engine` thêm tùy chọn SQLite; `backend/main.py:create_app` gọi `Base.metadata.create_all`. `.env.example`, runbook và worker vẫn định hướng PostgreSQL, đặc biệt `ImageTryOnRepository.claim` dùng `with_for_update(skip_locked=True)`. Cần sửa mặc định hoặc yêu cầu cấu hình PostgreSQL rõ ràng trước khi vận hành worker đa tiến trình. SQLite riêng của `backend/garment3d` là hệ lưu trữ khác.
- **API và schema:** merge thêm `fit/evaluator.py:GeometryFitEvaluator`, thuật toán M4 và interface; không thấy adapter từ `backend/main.py` hoặc `backend/services/orchestrator.py`. `/api/tryon/fit` vẫn gọi `MockProvider.fit`, nhãn và score chỉ là mock. `ImageTryOnResult` chưa có fit score, vùng fit, size hoặc heatmap. Nếu nối M4 vào web cần thống nhất contract M3–M4–M5; không tự diễn giải kết quả AI như dữ liệu thật.
- **Mô phỏng vải:** merge thêm `garment/simulation/simulator.py:ClothSimulator` và `blender_cloth_sim.py`, nhưng worker thử đồ ảnh gọi `compose_tryon.py`. `simulate_cloth=true` bị từ chối bằng `SIMULATION_UNAVAILABLE`; báo cáo luôn `simulation_ran=false`. Frontend `imageTryOnApi.create` không gửi cờ này. Cần M2 hiệu chuẩn solver trên mesh tái dựng, rồi M3 nối worker và M5 hiển thị trạng thái thật.
- **Đơn vị và hệ trục:** contract hiện yêu cầu m nội bộ, cm ở API, Y-up và +Z forward; worker kiểm tra frame của body và metadata áo. Tương thích của solver M2 mới với GLB từ ảnh và khả năng giữ vật liệu/texture sau mô phỏng: chưa kiểm tra runtime.
- **Asset và dữ liệu:** merge không thêm weights/checkpoint/GLB vào danh sách file của merge commit. Kho `data/assets/` giữ ignore theo thay đổi sẵn của người dùng. Khả năng dọn asset, giới hạn kích thước GLB sau mô phỏng: chưa kiểm tra.
- **Xung đột semantic đã xử lý:** xóa Rule 05 trái với chỉ thị người dùng; AGENTS mới tham chiếu memory chưa tồn tại. Đã khôi phục Rule 05, tạo memory tại máy hiện tại và bổ sung cách khởi tạo ở checkout mới.

## Xác minh và bàn giao

- `git diff --check` trên working tree sau chỉnh lý: không báo lỗi khoảng trắng.
- Chưa chạy test (Chờ User xác nhận). Chưa có bằng chứng chạy PostgreSQL, Blender, worker, UI hoặc bộ test sau merge; ba nhận định trên là rà soát tĩnh.
- M3: chốt chính sách `DATABASE_URL` PostgreSQL và migration; thiết kế adapter/contract cho fit và simulation, bổ sung test tích hợp.
- M2: xác nhận solver chạy được trên GLB áo tái dựng, đúng m/Y-up/+Z và giữ texture; làm rõ lỗi/timeout.
- M4: cung cấp ánh xạ kết quả `GeometryFitEvaluator` sang API, yêu cầu dữ liệu body/garment và giới hạn độ tin cậy AI.
- M5: nối dữ liệu fit/simulation vào trang thử đồ ảnh sau khi contract backend được chốt; giữ nhãn mock/real rõ ràng.
