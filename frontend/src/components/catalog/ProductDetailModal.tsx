import React, { useState } from 'react';
import { Product } from '../../data/mockProducts';

interface ProductDetailModalProps {
  product: Product;
  onClose: () => void;
  onSelectProductForTryOn: (product: Product, size?: string) => void;
}

export const ProductDetailModal: React.FC<ProductDetailModalProps> = ({
  product,
  onClose,
  onSelectProductForTryOn,
}) => {
  const [selectedSize, setSelectedSize] = useState<string>(product.sizes[0] || 'M');
  const [selectedColor, setSelectedColor] = useState<string>(product.colors[0]?.name || '');
  const [activeThumbIndex, setActiveThumbIndex] = useState<number>(0);
  const [addedToCart, setAddedToCart] = useState<boolean>(false);

  // 4 curated gallery angles matching the design
  const galleryImages = [
    {
      label: 'Mặt trước',
      url: product.imageUrl,
    },
    {
      label: 'Mặt sau',
      url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDNF0MBVOtBwrL7nvJKDK2sQAxPIJGrkEQZFH0727_0ebQTcCY_JxMCCkmpQz3xx1SBr-OsAKmLiW9cr8JvZvH7aN9h-v9rjEY_DCyIL4ucf2EQ6PelrIAnF8vP056CpGebqh-84TtVCtcLjjFzi4_dQ18GzhYHo2cFYUDa1wITDa-OWRGox7gKwioFMyg9xKxr4IIylv3mbZFJwCABdBxojgy8ZqbnZp481Jtm7nHnr8lFzeN04i_OSg',
    },
    {
      label: 'Chất vải',
      url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAqd48qLPVC0rcImqFtSwTXGbgO-dUNwS4NG-1-dAQgonX9EnjvDDf5O9MSHBNJu9FByEJZpL83UVS2fIdNCpXnu5W9FHDm47qWVwNknDCdneHiWWd_NQ-9sF_R3ncfzUCSpcOkdA0VTdZ-3ZD-XS9y9RSbWuA_-N0G7hV2urqYyG-F790CyYaUEkmQD3xP9AINQlFK7UgDhgInjfhPRTqz1AJBiTz_-miWT_K1C5QSNAcu4rci9zxq4A',
    },
    {
      label: 'Mẫu mặc',
      url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuD8ZOVz0jvOcmvEzRCSYFy_uL29KfkX9w0DPxL_nXTDZPOAKk79N4OHEHf65-tZ6jvkQDWn6j5_MYBkxjSrzMGzxQhj8bcWUqPijEzaZgREJrqXVpAF42PgIUW6kApDNGnl4pt1Gytvg3EN7lK_Ca_B9HPlQCBst6oOzj7bEUtfuAHa8jB9NTaDJvVjKCGnTofqO5k4BHqVkXSQva1TecQyJ2jtzRZaS1evE_QpU1oKY8ykM_YjlXC82A',
    },
  ];

  const currentDisplayImage = galleryImages[activeThumbIndex]?.url || product.imageUrl;

  return (
    <div className="vfit-product-modal-backdrop" onClick={onClose}>
      <div className="vfit-product-modal-box" onClick={(e) => e.stopPropagation()}>
        {/* Close Button */}
        <button
          type="button"
          className="vfit-product-modal-close"
          onClick={onClose}
          aria-label="Đóng"
        >
          ✕
        </button>

        <div className="vfit-product-detail-layout">
          {/* A. LEFT: GALLERY STAGING */}
          <div className="vfit-product-gallery">
            <div className="vfit-main-image-viewport">
              <img
                src={currentDisplayImage}
                alt={product.name}
              />

              {/* Floating AI Badge */}
              <div className="vfit-ai-tag-float">
                <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
                </svg>
                <span>AI READY • THỬ ĐỒ 3D</span>
              </div>

              {/* Floating Accuracy Tag */}
              <div className="vfit-ai-accuracy-float">
                <div className="vfit-pulse-dot" />
                <span>Độ chính xác dựng vải AI: 99.4%</span>
              </div>
            </div>

            {/* 4 Thumbnails */}
            <div className="vfit-thumbs-strip">
              {galleryImages.map((thumb, idx) => (
                <button
                  key={thumb.label}
                  type="button"
                  className={`vfit-thumb-btn ${activeThumbIndex === idx ? 'active' : ''}`}
                  onClick={() => setActiveThumbIndex(idx)}
                >
                  <img src={thumb.url} alt={thumb.label} />
                  <span className="vfit-thumb-label">{thumb.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* B. RIGHT: DETAILS & ACTIONS */}
          <div className="vfit-product-info-col">
            <div>
              <div className="vfit-product-collection-meta">
                <span>{product.tagline} • SIGNATURE 2026</span>
                <span style={{ color: 'var(--vfit-secondary)' }}>Mã: {product.id.toUpperCase()}</span>
              </div>

              <h2 className="vfit-product-modal-title">{product.name}</h2>

              {/* Rating */}
              <div className="vfit-product-rating-row">
                <div className="vfit-stars">★★★★★</div>
                <strong style={{ color: 'var(--vfit-on-surface)' }}>4.9</strong>
                <span>• 120 đánh giá thực tế từ khách hàng</span>
              </div>

              {/* Price Box */}
              <div className="vfit-product-price-box" style={{ margin: '1rem 0' }}>
                <div>
                  <span className="vfit-price-main">
                    {product.price.toLocaleString('vi-VN')}₫
                  </span>
                  {product.originalPrice && (
                    <span className="vfit-price-original">
                      {product.originalPrice.toLocaleString('vi-VN')}₫
                    </span>
                  )}
                </div>
                <span
                  style={{
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    padding: '0.3rem 0.65rem',
                    borderRadius: '9999px',
                    backgroundColor: 'var(--vfit-accent-lavender)',
                    color: 'var(--vfit-primary-container)',
                  }}
                >
                  FREESHIP TOÀN QUỐC
                </span>
              </div>

              {/* Fabric Specs */}
              <div className="vfit-fabric-specs" style={{ marginBottom: '1.25rem' }}>
                <div className="vfit-spec-item">
                  <span className="vfit-spec-title">Chất liệu</span>
                  <span className="vfit-spec-val">{product.material}</span>
                </div>
                <div className="vfit-spec-item">
                  <span className="vfit-spec-title">Co giãn</span>
                  <span className="vfit-spec-val">4 chiều Spandex</span>
                </div>
                <div className="vfit-spec-item">
                  <span className="vfit-spec-title">Trọng lượng</span>
                  <span className="vfit-spec-val">250 GSM dệt mật độ cao</span>
                </div>
                <div className="vfit-spec-item">
                  <span className="vfit-spec-title">Form dáng</span>
                  <span className="vfit-spec-val">Regular Fit chuẩn dáng</span>
                </div>
              </div>

              {/* Color Selection */}
              <div style={{ marginBottom: '1.25rem' }}>
                <div className="vfit-section-label">
                  <span>Màu sắc: <strong>{selectedColor}</strong></span>
                </div>
                <div style={{ display: 'flex', gap: '0.65rem' }}>
                  {product.colors.map((c) => (
                    <button
                      key={c.name}
                      type="button"
                      onClick={() => setSelectedColor(c.name)}
                      title={c.name}
                      style={{
                        width: '2.25rem',
                        height: '2.25rem',
                        borderRadius: '50%',
                        backgroundColor: c.hex,
                        border: selectedColor === c.name
                          ? '3px solid var(--vfit-focus-ring)'
                          : '1px solid var(--vfit-border-subtle)',
                        outline: selectedColor === c.name ? '2px solid #fff' : 'none',
                        cursor: 'pointer',
                        transition: 'transform 0.2s',
                        transform: selectedColor === c.name ? 'scale(1.15)' : 'none',
                      }}
                    />
                  ))}
                </div>
              </div>

              {/* Size Selection */}
              <div style={{ marginBottom: '1.25rem' }}>
                <div className="vfit-section-label">
                  <span>Kích cỡ: <strong>{selectedSize}</strong></span>
                  <span
                    style={{
                      fontSize: '0.75rem',
                      color: 'var(--vfit-focus-ring)',
                      fontWeight: 600,
                      cursor: 'pointer',
                      textDecoration: 'underline',
                    }}
                  >
                    Bảng số đo cơ thể (Size Guide)
                  </span>
                </div>
                <div className="vfit-size-pills">
                  {product.sizes.map((s) => (
                    <button
                      key={s}
                      type="button"
                      className={`vfit-size-pill-btn ${selectedSize === s ? 'active' : ''}`}
                      onClick={() => setSelectedSize(s)}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* CTAs */}
            <div className="vfit-action-stack">
              <button
                type="button"
                className="vfit-btn-try-now"
                onClick={() => {
                  onClose();
                  onSelectProductForTryOn(product, selectedSize);
                }}
              >
                <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
                </svg>
                <span>THỬ ĐỒ 3D NGAY VỚI TRANG PHỤC NÀY</span>
              </button>

              <button
                type="button"
                className="vfit-btn-secondary"
                style={{ width: '100%', height: '2.85rem' }}
                onClick={() => setAddedToCart(true)}
              >
                {addedToCart ? '✓ ĐÃ THÊM VÀO GIỎ HÀNG' : 'THÊM VÀO GIỎ HÀNG'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
