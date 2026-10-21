import React from 'react';

export const HowItWorksSection: React.FC = () => {
  return (
    <section className="vfit-section-bg">
      <div className="vfit-how-it-works-content" style={{ maxWidth: '1280px', margin: '0 auto', textAlign: 'center' }}>
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
          Tạo body, chọn ảnh trang phục và xem kết quả trong viewer 3D.
        </p>

        {/* 3 Steps Bento Grid */}
        <div className="vfit-bento-grid">
          {/* Step 1 */}
          <div className="vfit-bento-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="vfit-step-icon">01</div>
              <span className="vfit-step-num">01</span>
            </div>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 0.4rem 0', color: 'var(--vfit-on-surface)' }}>
                Thiết lập body 3D
              </h3>
              <p style={{ fontSize: '0.9rem', color: 'var(--vfit-secondary)', lineHeight: '1.6', margin: 0 }}>
                Nhập chiều cao và số đo cơ thể để tạo hoặc cập nhật mô hình body.
              </p>
            </div>
            <div style={{ marginTop: 'auto', paddingTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--vfit-primary-container)', fontSize: '0.8rem', fontWeight: 600 }}>
              <span>Số đo nhập theo centimet</span>
            </div>
          </div>

          {/* Step 2 */}
          <div className="vfit-bento-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="vfit-step-icon">02</div>
              <span className="vfit-step-num">02</span>
            </div>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 0.4rem 0', color: 'var(--vfit-on-surface)' }}>
                Tải ảnh trang phục
              </h3>
              <p style={{ fontSize: '0.9rem', color: 'var(--vfit-secondary)', lineHeight: '1.6', margin: 0 }}>
                Chọn ảnh mặt trước; ảnh mặt sau không bắt buộc. Có thể thêm áo và quần trong cùng một lượt.
              </p>
            </div>
            <div style={{ marginTop: 'auto', paddingTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--vfit-primary-container)', fontSize: '0.8rem', fontWeight: 600 }}>
              <span>Hỗ trợ ảnh JPG, PNG và WebP</span>
            </div>
          </div>

          {/* Step 3 */}
          <div className="vfit-bento-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="vfit-step-icon">03</div>
              <span className="vfit-step-num">03</span>
            </div>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 0.4rem 0', color: 'var(--vfit-on-surface)' }}>
                Xem kết quả 3D
              </h3>
              <p style={{ fontSize: '0.9rem', color: 'var(--vfit-secondary)', lineHeight: '1.6', margin: 0 }}>
                Xoay và quan sát cảnh body cùng trang phục đã ghép. Kết quả hiện tại là bản xem trước tĩnh.
              </p>
            </div>
            <div style={{ marginTop: 'auto', paddingTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--vfit-primary-container)', fontSize: '0.8rem', fontWeight: 600 }}>
              <span>Có thể xoay và phóng to bản xem trước</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
