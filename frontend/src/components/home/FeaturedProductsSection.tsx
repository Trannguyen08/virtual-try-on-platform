import React, { useState } from 'react';
import { MOCK_PRODUCTS, Product } from '../../data/mockProducts';

interface FeaturedProductsSectionProps {
  onSelectProductForTryOn: (product: Product) => void;
  onViewAllCatalog: () => void;
}

export const FeaturedProductsSection: React.FC<FeaturedProductsSectionProps> = ({
  onSelectProductForTryOn,
  onViewAllCatalog,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const categories = [
    { key: 'all', label: 'Tất cả' },
    { key: 't_shirt', label: 'Áo thun' },
    { key: 'shirt', label: 'Áo sơ mi' },
    { key: 'dress', label: 'Váy đầm' },
    { key: 'jacket', label: 'Áo khoác' },
  ];

  const filteredProducts =
    selectedCategory === 'all'
      ? MOCK_PRODUCTS
      : MOCK_PRODUCTS.filter((p) => p.category === selectedCategory);

  return (
    <section className="vfit-products-section">
      {/* Top Header & Tabs */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '1.5rem' }}>
        <div>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--vfit-primary-container)' }}>
            Lookbook Thịnh Hành
          </span>
          <h2 style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--vfit-on-surface)', letterSpacing: '-0.025em', margin: '0.35rem 0 0 0' }}>
            SẢN PHẨM NỔI BẬT
          </h2>
        </div>

        {/* Category Tabs */}
        <div className="vfit-category-tabs">
          {categories.map((cat) => (
            <button
              key={cat.key}
              type="button"
              className={`vfit-tab-btn ${selectedCategory === cat.key ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat.key)}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Products Grid */}
      <div className="vfit-product-grid">
        {filteredProducts.slice(0, 4).map((product) => (
          <div key={product.id} className="vfit-product-card">
            {/* Thumbnail */}
            <div className="vfit-product-thumb">
              <img src={product.imageUrl} alt={product.name} />

              {/* Material Pill */}
              <span
                style={{
                  position: 'absolute',
                  bottom: '0.75rem',
                  left: '0.75rem',
                  backgroundColor: 'rgba(2, 4, 9, 0.75)',
                  backdropFilter: 'blur(6px)',
                  color: '#ffffff',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  padding: '0.25rem 0.65rem',
                  borderRadius: '9999px',
                }}
              >
                {product.material}
              </span>

              {/* Hot/New Badge */}
              {product.isHot && (
                <span
                  style={{
                    position: 'absolute',
                    top: '0.75rem',
                    left: '0.75rem',
                    backgroundColor: 'var(--vfit-destructive-crimson)',
                    color: '#ffffff',
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    padding: '0.2rem 0.5rem',
                    borderRadius: '4px',
                    textTransform: 'uppercase',
                  }}
                >
                  HOT
                </span>
              )}
            </div>

            {/* Info */}
            <div className="vfit-product-info">
              <div>
                <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--vfit-secondary)', letterSpacing: '0.05em' }}>
                  {product.tagline}
                </span>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--vfit-on-surface)', margin: '0.25rem 0 0.5rem 0', lineHeight: '1.3' }}>
                  {product.name}
                </h3>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
                  <span style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--vfit-primary-container)' }}>
                    {product.price.toLocaleString('vi-VN')}₫
                  </span>
                  {product.originalPrice && (
                    <span style={{ fontSize: '0.85rem', color: 'var(--vfit-outline)', textDecoration: 'line-through' }}>
                      {product.originalPrice.toLocaleString('vi-VN')}₫
                    </span>
                  )}
                </div>
              </div>

              {/* Action Button */}
              <button
                type="button"
                className="vfit-btn-primary"
                style={{ height: '2.65rem', fontSize: '0.85rem', marginTop: '1rem', borderRadius: 'var(--vfit-radius-md)' }}
                onClick={() => onSelectProductForTryOn(product)}
              >
                <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
                </svg>
                <span>THỬ NGAY</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* View All Button */}
      <div style={{ textAlign: 'center', marginTop: '3rem' }}>
        <button
          type="button"
          className="vfit-btn-secondary"
          style={{ display: 'inline-flex', padding: '0 2.5rem' }}
          onClick={onViewAllCatalog}
        >
          <span>Khám phá toàn bộ danh mục ({MOCK_PRODUCTS.length} trang phục)</span>
          <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </section>
  );
};
