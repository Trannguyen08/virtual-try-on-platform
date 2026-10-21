import React from 'react';

export const HowItWorksSection: React.FC = () => {
  return (
    <section className="vfit-section-bg">
      <div style={{ maxWidth: '1280px', margin: '0 auto', textAlign: 'center' }}>
        <span
          style={{
            fontSize: '0.75rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            color: 'var(--vfit-primary-container)',
            backgroundColor: 'var(--vfit-surface-container-highest)',
            padding: '0.35rem 0.85rem',
            borderRadius: '9999px',
          }}
        >
          Quy trình đơn giản
        </span>
        <h2
          style={{
            fontSize: '2.25rem',
            fontWeight: 800,
            color: 'var(--vfit-on-surface)',
            letterSpacing: '-0.025em',
            margin: '0.75rem 0 0.5rem 0',
          }}
        >
          CÁCH HOẠT ĐỘNG
        </h2>
        <p style={{ color: 'var(--vfit-secondary)', fontSize: '1rem', maxWidth: '36rem', margin: '0 auto' }}>
          Chỉ 3 bước trực quan để trải nghiệm và tìm ra bộ trang phục hoàn hảo tôn vinh dáng vẻ của bạn.
        </p>

        {/* 3 Steps Bento Grid */}
        <div className="vfit-bento-grid">
          {/* Step 1 */}
          <div className="vfit-bento-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="vfit-step-icon">📸</div>
              <span className="vfit-step-num">01</span>
            </div>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 0.4rem 0', color: 'var(--vfit-on-surface)' }}>
                Upload Ảnh Toàn Thân
              </h3>
              <p style={{ fontSize: '0.9rem', color: 'var(--vfit-secondary)', lineHeight: '1.6', margin: 0 }}>
                Tải ảnh đứng toàn thân rõ nét hoặc chụp từ camera. Đứng thẳng tự nhiên để AI phân tích chuẩn xác form dáng người và số đo.
              </p>
            </div>
            <div style={{ marginTop: 'auto', paddingTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--vfit-primary-container)', fontSize: '0.8rem', fontWeight: 600 }}>
              <span>🔒 Bảo mật quyền riêng tư 100%</span>
            </div>
          </div>

          {/* Step 2 */}
          <div className="vfit-bento-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="vfit-step-icon">👗</div>
              <span className="vfit-step-num">02</span>
            </div>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 0.4rem 0', color: 'var(--vfit-on-surface)' }}>
                Chọn Trang Phục & Size
              </h3>
              <p style={{ fontSize: '0.9rem', color: 'var(--vfit-secondary)', lineHeight: '1.6', margin: 0 }}>
                Duyệt qua catalog đa dạng áo thun, sơ mi, đầm váy, áo khoác. Chọn kích cỡ S, M, L, XL để xem độ vừa vặn từng phân vùng cơ thể.
              </p>
            </div>
            <div style={{ marginTop: 'auto', paddingTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--vfit-primary-container)', fontSize: '0.8rem', fontWeight: 600 }}>
              <span>⚡ Đánh giá 4 vùng: ngực, eo, hông, vai</span>
            </div>
          </div>

          {/* Step 3 */}
          <div className="vfit-bento-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="vfit-step-icon">🪄</div>
              <span className="vfit-step-num">03</span>
            </div>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 0.4rem 0', color: 'var(--vfit-on-surface)' }}>
                Xem Kết Quả Trong 3s
              </h3>
              <p style={{ fontSize: '0.9rem', color: 'var(--vfit-secondary)', lineHeight: '1.6', margin: 0 }}>
                AI tạo mô hình 3D tương tác chân thực với ánh sáng studio, nếp gấp vải tự nhiên và hiệu ứng tôn dáng như đứng trước gương phòng thử.
              </p>
            </div>
            <div style={{ marginTop: 'auto', paddingTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--vfit-primary-container)', fontSize: '0.8rem', fontWeight: 600 }}>
              <span>🌐 Tương tác 3D WebGL xoay 360°</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
