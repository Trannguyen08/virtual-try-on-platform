import React from 'react';

interface HeroSectionProps {
  onStartTryOn: () => void;
  onExploreCatalog: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onStartTryOn, onExploreCatalog }) => {
  return (
    <section className="vfit-hero">
      {/* Background ambient spotlight */}
      <div className="vfit-ambient-glow-1" style={{ top: '10%', left: '40%' }} />

      <div className="vfit-hero-grid">
        {/* Left Column: Value Proposition */}
        <div>
          {/* Trend Badge */}
          <div className="vfit-tag-trend">
            <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2l2.4 7.2h7.6l-6 4.8 2.4 7.2-6-4.8-6 4.8 2.4-7.2-6-4.8h7.6z" />
            </svg>
            <span>PHÒNG THỬ ĐỒ 3D</span>
          </div>

          {/* Headline */}
          <h1 className="vfit-hero-title">
            XEM TRANG PHỤC <br />
            <span className="vfit-gradient-text">TRÊN BODY 3D</span>
          </h1>

          <p className="vfit-hero-desc">
            Tạo vóc dáng 3D theo thông số của bạn, tải ảnh trang phục và xem bản phối trong không gian 3D.
          </p>

          {/* Primary CTA Group */}
          <div className="vfit-btn-group">
            <button
              type="button"
              className="vfit-btn-primary"
              style={{ width: 'auto', padding: '0 2rem', height: '3.25rem' }}
              onClick={onStartTryOn}
            >
              <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
              </svg>
              <span>BẮT ĐẦU THỬ ĐỒ</span>
              <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>

            <button
              type="button"
              className="vfit-btn-secondary"
              onClick={onExploreCatalog}
            >
              <span>Xem bộ sưu tập</span>
            </button>
          </div>

          {/* Commitment Checklist */}
          <div className="vfit-checklist-box">
            <div className="vfit-checklist-title">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-3zm-2 16l-4-4 1.41-1.41L10 15.17l6.59-6.59L18 10l-8 8z" />
              </svg>
              <span>Quy trình thử đồ</span>
            </div>
            <div className="vfit-checklist-items">
              <div>
                <span className="vfit-check-dot" />
                Tạo body theo thông số
              </div>
              <div>
                <span className="vfit-check-dot" />
                Chọn sản phẩm ưng ý
              </div>
              <div>
                <span className="vfit-check-dot" />
                Xem kết quả sau khi xử lý
              </div>
            </div>
          </div>

        </div>

        {/* Sample fashion image */}
        <div className="vfit-showcase-container">
          <div className="vfit-showcase-card">
            <img
              src="https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=900&auto=format&fit=crop&q=80"
              alt="Mẫu trang phục minh họa"
              className="vfit-showcase-img"
            />
          </div>
          <span className="vfit-showcase-caption">Ảnh minh họa</span>
        </div>
      </div>
    </section>
  );
};
