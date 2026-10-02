import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="vfit-footer">
      <div className="vfit-footer-inner">
        {/* Col 1 */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '1rem' }}>
            <div className="vfit-brand-logo-icon" style={{ width: '2rem', height: '2rem', fontSize: '1rem' }}>V</div>
            <span style={{ fontSize: '1.2rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#ffffff' }}>
              AI TRY-ON
            </span>
          </div>
          <p style={{ color: '#94a3b8', fontSize: '0.9rem', lineHeight: '1.6', maxWidth: '320px' }}>
            Nền tảng phòng thử đồ ảo 3D ứng dụng trí tuệ nhân tạo. Tái tạo vóc dáng người dùng chuẩn xác, gợi ý kích thước trang phục tối ưu.
          </p>
          <div style={{ marginTop: '1.25rem', color: '#64748b', fontSize: '0.8rem' }}>
            © 2026 Virtual Try-On Platform. All rights reserved.
          </div>
        </div>

        {/* Col 2 */}
        <div>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '1rem', color: '#ffffff' }}>Khám Phá</h4>
          <a href="#catalog" className="vfit-footer-link">Sản phẩm nổi bật</a>
          <a href="#try-on" className="vfit-footer-link">Thử đồ 3D thời gian thực</a>
          <a href="#size-chart" className="vfit-footer-link">Bảng thông số kích thước</a>
          <a href="#lookbook" className="vfit-footer-link">Bộ sưu tập Runway</a>
        </div>

        {/* Col 3 */}
        <div>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '1rem', color: '#ffffff' }}>Công Nghệ AI</h4>
          <a href="#smplx" className="vfit-footer-link">Mô hình SMPL-X 3D</a>
          <a href="#mediapipe" className="vfit-footer-link">MediaPipe AI Pose</a>
          <a href="#cloth" className="vfit-footer-link">Mô phỏng trọng lực sợi vải</a>
          <a href="#accuracy" className="vfit-footer-link">Độ chính xác số đo 99%</a>
        </div>

        {/* Col 4 */}
        <div>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '1rem', color: '#ffffff' }}>Bảo Mật & Hỗ Trợ</h4>
          <a href="#privacy" className="vfit-footer-link">Mã hóa dữ liệu 256-bit</a>
          <a href="#terms" className="vfit-footer-link">Điều khoản dịch vụ</a>
          <a href="#contact" className="vfit-footer-link">Liên hệ đội ngũ hỗ trợ</a>
          <a href="#faq" className="vfit-footer-link">Câu hỏi thường gặp</a>
        </div>
      </div>
    </footer>
  );
};
