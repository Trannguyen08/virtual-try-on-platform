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
            <span>CÔNG NGHỆ THỬ ĐỒ ẢO THỜI TRANG 4.0</span>
          </div>

          {/* Headline */}
          <h1 className="vfit-hero-title">
            THỬ ĐỒ ẢO VỚI AI <br />
            <span className="vfit-gradient-text">TRÊN CHÍNH BẠN</span>
          </h1>

          <p className="vfit-hero-desc">
            Xem trước trang phục trên hình ảnh và vóc dáng 3D của bạn trước khi mua. Chuẩn form dáng, chân thực từng nếp vải với công nghệ AI tái tạo hình thể tiên tiến.
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
              <span>Trải nghiệm trực tuyến mượt mà</span>
            </div>
            <div className="vfit-checklist-items">
              <div>
                <span className="vfit-check-dot" />
                Upload ảnh toàn thân
              </div>
              <div>
                <span className="vfit-check-dot" />
                Chọn sản phẩm ưng ý
              </div>
              <div>
                <span className="vfit-check-dot" />
                AI tạo kết quả trong 3s
              </div>
            </div>
          </div>

          {/* Trust Metrics */}
          <div className="vfit-metrics-row">
            <div>
              <div className="vfit-metric-num">99%</div>
              <div className="vfit-metric-label">Chuẩn tỷ lệ cơ thể</div>
            </div>
            <div>
              <div className="vfit-metric-num">50.000+</div>
              <div className="vfit-metric-label">Lượt thử mỗi ngày</div>
            </div>
            <div>
              <div className="vfit-metric-num" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                4.9
                <span style={{ color: '#f59e0b', fontSize: '1.25rem' }}>★</span>
              </div>
              <div className="vfit-metric-label">Đánh giá hài lòng</div>
            </div>
          </div>
        </div>

        {/* Right Column: Hologram Stage Showcase */}
        <div className="vfit-showcase-container">
          <div className="vfit-showcase-card">
            <img
              src="https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=900&auto=format&fit=crop&q=80"
              alt="AI Virtual Try-On Model Showcase"
              className="vfit-showcase-img"
            />

            {/* AI Active Indicator */}
            <div className="vfit-hud-badge-top">
              <span className="vfit-pulse-dot" />
              <span>AI Engine Active</span>
            </div>

            {/* Fit Accuracy HUD */}
            <div className="vfit-hud-accuracy">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: '#b6c4ff', textTransform: 'uppercase', fontSize: '0.7rem' }}>Fit Accuracy</span>
                <span style={{ color: '#34d399', fontWeight: 700 }}>98%</span>
              </div>
              <div style={{ width: '100%', height: '4px', backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: '4px', marginTop: '0.4rem', overflow: 'hidden' }}>
                <div style={{ width: '98%', height: '100%', background: 'linear-gradient(90deg, #3d7eff, #34d399)' }} />
              </div>
            </div>

            {/* Bottom HUD Card */}
            <div className="vfit-hud-bottom">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#bfc2ff' }}>
                  Haute Couture Capsule
                </span>
                <span style={{ fontSize: '0.75rem', backgroundColor: '#080a61', padding: '0.15rem 0.5rem', borderRadius: '9999px', border: '1px solid #517aff' }}>
                  Live Fit
                </span>
              </div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, letterSpacing: '-0.01em' }}>
                Dáng Chuẩn Runway Tailored
              </div>
              <div style={{ display: 'flex', gap: '1rem', color: '#cbd5e1', fontSize: '0.8rem', marginTop: '0.4rem' }}>
                <span>✨ Lụa Satin Cao Cấp</span>
                <span>📐 Size M (Chuẩn 99%)</span>
              </div>
            </div>
          </div>

          {/* Floating 360 Badge */}
          <div className="vfit-floating-badge">
            <div
              style={{
                width: '2.5rem',
                height: '2.5rem',
                borderRadius: '50%',
                backgroundColor: 'var(--vfit-secondary-container)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--vfit-primary-container)',
                fontSize: '1.25rem',
              }}
            >
              🔄
            </div>
            <div>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--vfit-on-surface)' }}>
                Xoay 360° Đa Chiều
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--vfit-secondary)' }}>
                Mô phỏng trọng lực nếp vải
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
