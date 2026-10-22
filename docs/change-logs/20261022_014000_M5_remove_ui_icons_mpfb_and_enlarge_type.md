# Change Impact Log: Bỏ icon, chữ MPFB và tăng cỡ chữ giao diện

## Vai trò và mục đích

- Vai trò: M5 (frontend).
- Mục đích: làm giao diện ít chi tiết trang trí hơn, bỏ tên MPFB khỏi nội dung người dùng nhìn thấy và tăng nhẹ khả năng đọc.
- Thời gian: 2026-10-22 01:40 Asia/Saigon.

## File thay đổi

- `frontend/src/styles/layout.css`: font gốc 16px → 17px, cỡ rem tăng nhẹ; ẩn SVG trang trí, bỏ các wrapper icon và tăng cỡ một số nhãn nhỏ. Giữ ảnh sản phẩm/3D và logo chữ V.
- `frontend/src/styles/history.css`: đổi lớp nút thao tác lịch sử từ nút icon vuông sang nút chữ có padding và chiều rộng tối thiểu.
- `frontend/src/hooks/useGarmentProducts.ts`: đổi các trạng thái kho có chữ MPFB/thuật ngữ refit sang thông báo tiếng Việt; giữ nguyên đường dẫn ảnh nội bộ.
- `frontend/src/components/catalog/ProductDetailModal.tsx`: bỏ MPFB khỏi mô tả và bỏ ký tự trang trí; giữ nội dung sản phẩm.
- `frontend/src/components/tryon/UploadStep.tsx`: bỏ emoji/nhãn MPFB2 và chỉnh câu mô tả mẫu cơ thể.
- `frontend/src/pages/tryon/ImageTryOnPage.tsx`: bỏ emoji trong thông báo, bước tiến trình và nút tải; đổi thông báo lỗi mặc định sang “mẫu cơ thể”.
- `frontend/src/pages/catalog/CatalogPage.tsx`: bỏ emoji và SVG hiển thị, giữ nhãn thao tác bằng chữ.
- `frontend/src/pages/history/HistoryPage.tsx`: bỏ emoji trạng thái rỗng và đổi nút đóng thành chữ.
- `frontend/src/components/tryon/BodyBuilderStep.tsx`: bỏ thuộc tính emoji khỏi nhãn slider và bỏ biểu tượng trong nút thao tác.
- `frontend/src/components/home/HowItWorksSection.tsx`: thay emoji bằng số bước và bỏ ký tự trang trí.
- `frontend/src/components/ai/AiSizeAdvisorModal.tsx`: bỏ emoji/biểu tượng và thay nội dung tiêu đề bằng chữ.
- `frontend/src/components/auth/ForgotPasswordModal.tsx`: bỏ emoji và ký tự đóng dạng icon.
- `frontend/src/components/chat/AiStylistChatWidget.tsx`: bỏ emoji trong tin nhắn mẫu/nhãn và thay nút gửi bằng chữ.
- `frontend/src/components/tryon/SelectGarmentStep.tsx`: bỏ emoji và ký tự mũi tên, giữ nút xác nhận bằng nhãn chữ.
- `frontend/src/components/tryon/ProcessingStep.tsx`: bỏ emoji khỏi trạng thái và đổi nhãn kỹ thuật thành nội dung dễ hiểu.
- `frontend/src/components/tryon/BodyMorphingPanel.tsx`: bỏ emoji và ký hiệu trang trí khỏi nhãn.
- `frontend/src/components/tryon/ConfirmTryOnStep.tsx`: bỏ các emoji và hai vùng trang trí chỉ chứa icon.
- `frontend/src/components/history/CompareModal.tsx`: bỏ emoji/checkmark khỏi nhãn và nút đóng.
- `frontend/src/components/tryon/InteractiveViewer3DStep.tsx`: bỏ emoji/mũi tên/checkmark khỏi tiêu đề và thao tác.
- `frontend/src/pages/tryon/TryOnPage.tsx`: dùng chữ “Xong” cho bước xong thay checkmark.
- `frontend/src/pages/tryon/OutfitTryOnPage.tsx`: bỏ mũi tên/checkmark trong nút và bước hoàn tất.
- `frontend/src/components/tryon/GeneratedBodyViewer.tsx`: bỏ mũi tên và dùng “mẫu cơ thể” thay “body” trên nút.
- `frontend/src/components/GarmentImageInputs.tsx`: bỏ checkmark trang trí trong thông báo tải ảnh.
- `frontend/src/pages/auth/LoginPage.tsx`, `frontend/src/pages/auth/RegisterPage.tsx`: thay biểu tượng hiện/ẩn mật khẩu bằng nhãn “Hiện/Ẩn”.
- `frontend/src/components/history/HistoryCard.tsx`: đổi thao tác tải/thử lại/xóa thành nút chữ.
- `frontend/src/components/history/HistoryToolbar.tsx`: bỏ ký tự X khỏi nút xóa bộ lọc.

## Ảnh hưởng

- API/schema: không đổi; không có request hay response nào bị sửa.
- Đơn vị/hệ trục: không đổi.
- Database/asset: không đổi; giữ các đường dẫn hình minh họa nội bộ có chuỗi `mpfb` để không làm hỏng asset.
- Module: chỉ M5. Không chỉnh backend, dữ liệu catalog hay contract tích hợp.
- Xung đột: chưa xác nhận xung đột. Có nguy cơ CSS ẩn SVG toàn cục làm mất biểu tượng SVG nào được dùng như nội dung; rà soát hiện tại thấy các SVG trong `frontend/src` là biểu tượng giao diện. Ảnh sản phẩm và mô hình 3D không bị CSS này ảnh hưởng.

## Kiểm thử

- Chưa chạy frontend build/test hoặc xem giao diện trên trình duyệt theo Rule 01.
- Đã rà nội dung JSX/TSX bằng tìm kiếm chỉ đọc: các chuỗi MPFB còn lại là tên đường dẫn/định danh nội bộ và chú thích code, không phải nhãn render trực tiếp.

## Bàn giao

- Owner tiếp theo: M5; cần xem giao diện desktop/mobile để kiểm tra độ rộng các nút chữ mới và nhãn “Xong” trong bước tiến trình.
- Cần build frontend sau khi được phép chạy lệnh; nếu có SVG được dùng như hình minh họa nội dung trong tương lai, cần loại khỏi quy tắc ẩn SVG toàn cục.
