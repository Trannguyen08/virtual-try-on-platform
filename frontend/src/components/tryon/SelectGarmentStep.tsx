import React, { useState } from 'react';
import { MOCK_PRODUCTS, Product } from '../../data/mockProducts';

interface SelectGarmentStepProps {
  initialGarment: Product | null;
  onBack: () => void;
  onConfirm: (garment: Product, selectedSize: string) => void;
}

export const SelectGarmentStep: React.FC<SelectGarmentStepProps> = ({
  initialGarment,
  onBack,
  onConfirm,
}) => {
  const [selectedGarment, setSelectedGarment] = useState<Product>(
    initialGarment || MOCK_PRODUCTS[0]
  );
  const [selectedSize, setSelectedSize] = useState<string>('M');

  const sizes = ['S', 'M', 'L', 'XL'];

  const getSizeFeedback = (size: string) => {
    if (size === 'S') return { text: 'Ôm sát (Tight fit)', color: '#dc2626', bg: '#fee2e2' };
    if (size === 'M') return { text: 'Vừa vặn hoàn hảo (Optimal fit)', color: '#059669', bg: '#d1fae5' };
    return { text: 'Thoải mái / Rộng (Loose fit)', color: '#d97706', bg: '#fef3c7' };
  };

  const feedback = getSizeFeedback(selectedSize);

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div style={{ backgroundColor: 'var(--vfit-surface-card)', borderRadius: 'var(--vfit-radius-xl)', padding: '2rem', boxShadow: '0 2px 10px rgba(8,10,97,0.03)' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', padding: '0.25rem 0.75rem', borderRadius: '9999px', backgroundColor: 'var(--vfit-secondary-container)', color: 'var(--vfit-primary-container)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.5rem' }}>
          <span>👗 Bước 2 • Chọn trang phục & Size</span>
        </div>

        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--vfit-on-surface)', margin: '0 0 0.5rem 0', letterSpacing: '-0.02em' }}>
          XÁC NHẬN TRANG PHỤC VÀ SIZE THỬ
        </h2>
        <p style={{ color: 'var(--vfit-secondary)', fontSize: '0.9rem', margin: '0 0 1.5rem 0' }}>
          Chọn món đồ và kích cỡ bạn muốn AI mô phỏng mặc thử trên vóc dáng của bạn.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '2rem', alignItems: 'start' }}>
          {/* Garment Showcase Card */}
          <div style={{ borderRadius: 'var(--vfit-radius-lg)', overflow: 'hidden', border: '1px solid var(--vfit-border-subtle)', backgroundColor: '#ffffff' }}>
            <div style={{ height: '320px', position: 'relative', overflow: 'hidden' }}>
              <img
                src={selectedGarment.imageUrl}
                alt={selectedGarment.name}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
              <span
                style={{
                  position: 'absolute',
                  bottom: '1rem',
                  left: '1rem',
                  backgroundColor: 'rgba(6, 10, 19, 0.8)',
                  backdropFilter: 'blur(4px)',
                  color: '#ffffff',
                  fontSize: '0.75rem',
                  padding: '0.25rem 0.65rem',
                  borderRadius: '9999px',
                }}
              >
                Chất liệu: {selectedGarment.material}
              </span>
            </div>

            <div style={{ padding: '1.25rem' }}>
              <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--vfit-secondary)' }}>
                {selectedGarment.tagline}
              </span>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--vfit-on-surface)', margin: '0.25rem 0' }}>
                {selectedGarment.name}
              </h3>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--vfit-primary-container)' }}>
                {selectedGarment.price.toLocaleString('vi-VN')}₫
              </div>
            </div>
          </div>

          {/* Configuration Panel */}
          <div>
            {/* Quick Switch Garments */}
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--vfit-on-surface)', marginBottom: '0.5rem' }}>
                Đổi mẫu khác nhanh:
              </label>
              <div style={{ display: 'flex', gap: '0.5rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
                {MOCK_PRODUCTS.slice(0, 4).map((g) => (
                  <button
                    key={g.id}
                    type="button"
                    onClick={() => setSelectedGarment(g)}
                    style={{
                      border: selectedGarment.id === g.id ? '2px solid var(--vfit-focus-ring)' : '1px solid var(--vfit-border-subtle)',
                      borderRadius: '0.5rem',
                      padding: '0.25rem',
                      background: 'none',
                      cursor: 'pointer',
                      flexShrink: 0,
                    }}
                  >
                    <img
                      src={g.imageUrl}
                      alt={g.name}
                      style={{ width: '50px', height: '65px', objectFit: 'cover', borderRadius: '4px' }}
                    />
                  </button>
                ))}
              </div>
            </div>

            {/* Size Selector */}
            <div style={{ marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <label style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--vfit-on-surface)' }}>
                  Chọn kích cỡ (Size)
                </label>
                <span style={{ fontSize: '0.75rem', color: 'var(--vfit-focus-ring)', fontWeight: 600 }}>
                  Size khuyên dùng: M
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.65rem' }}>
                {sizes.map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => setSelectedSize(s)}
                    style={{
                      height: '3rem',
                      borderRadius: 'var(--vfit-radius-md)',
                      border: 'none',
                      backgroundColor: selectedSize === s ? 'var(--vfit-primary-container)' : 'var(--vfit-surface-container)',
                      color: selectedSize === s ? '#ffffff' : 'var(--vfit-on-surface)',
                      fontWeight: 800,
                      fontSize: '1.1rem',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      boxShadow: selectedSize === s ? '0 4px 12px rgba(8,10,97,0.2)' : 'none',
                    }}
                  >
                    {s}
                  </button>
                ))}
              </div>

              {/* Dynamic Fit Feedback Badge */}
              <div
                style={{
                  marginTop: '0.85rem',
                  padding: '0.6rem 0.85rem',
                  borderRadius: '0.5rem',
                  backgroundColor: feedback.bg,
                  color: feedback.color,
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                }}
              >
                <span>💡</span>
                <span>{feedback.text}</span>
              </div>
            </div>

            {/* Action Buttons */}
            <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
              <button
                type="button"
                className="vfit-btn-secondary"
                style={{ flex: 1 }}
                onClick={onBack}
              >
                ← Quay lại ảnh
              </button>
              <button
                type="button"
                className="vfit-btn-primary"
                style={{ flex: 2, height: '3.25rem' }}
                onClick={() => onConfirm(selectedGarment, selectedSize)}
              >
                <span>XÁC NHẬN THỬ ĐỒ 3D</span>
                <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
