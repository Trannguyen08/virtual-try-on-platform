import React, { useMemo, useState } from 'react';
import { MOCK_PRODUCTS, Product } from '../../data/mockProducts';

interface CatalogPageProps {
  onSelectProductForTryOn: (product: Product) => void;
  onNavigateHome: () => void;
}

export const CatalogPage: React.FC<CatalogPageProps> = ({
  onSelectProductForTryOn,
  onNavigateHome,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedGender, setSelectedGender] = useState<string>('all');
  const [selectedSize, setSelectedSize] = useState<string>('all');
  const [selectedColor, setSelectedColor] = useState<string>('all');
  const [maxPrice, setMaxPrice] = useState<number>(2000000);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [sortBy, setSortBy] = useState<'newest' | 'price-asc' | 'price-desc' | 'popular'>('popular');

  // Categories list with count
  const categories = [
    { key: 'all', label: 'Tất cả' },
    { key: 't_shirt', label: 'Áo thun' },
    { key: 'shirt', label: 'Áo sơ mi' },
    { key: 'dress', label: 'Váy đầm' },
    { key: 'jacket', label: 'Áo khoác' },
  ];

  const sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL'];

  const colorSwatches = [
    { name: 'all', hex: '', label: 'Tất cả' },
    { name: 'Đen Obsidian', hex: '#0a050d', label: 'Đen' },
    { name: 'Trắng Chalk', hex: '#f5f5f5', label: 'Trắng' },
    { name: 'Xanh Midnight Navy', hex: '#03035e', label: 'Navy' },
    { name: 'Be Silk', hex: '#f3ebd8', label: 'Be' },
    { name: 'Xanh Olive', hex: '#4b5320', label: 'Olive' },
    { name: 'Hồng Pastel', hex: '#f9d5e5', label: 'Hồng' },
  ];

  const handleResetFilters = () => {
    setSelectedCategory('all');
    setSelectedGender('all');
    setSelectedSize('all');
    setSelectedColor('all');
    setMaxPrice(2000000);
    setSearchQuery('');
    setSortBy('popular');
  };

  // Filter and Sort Logic
  const filteredProducts = useMemo(() => {
    return MOCK_PRODUCTS.filter((product) => {
      // Category filter
      if (selectedCategory !== 'all' && product.category !== selectedCategory) {
        return false;
      }
      // Gender filter
      if (selectedGender !== 'all' && product.gender !== selectedGender) {
        return false;
      }
      // Size filter
      if (selectedSize !== 'all' && !product.sizes.includes(selectedSize as any)) {
        return false;
      }
      // Color filter
      if (selectedColor !== 'all' && !product.colors.some((c) => c.name === selectedColor)) {
        return false;
      }
      // Price filter
      if (product.price > maxPrice) {
        return false;
      }
      // Search query
      if (searchQuery.trim() !== '') {
        const q = searchQuery.toLowerCase();
        return (
          product.name.toLowerCase().includes(q) ||
          product.categoryLabel.toLowerCase().includes(q) ||
          product.material.toLowerCase().includes(q)
        );
      }
      return true;
    }).sort((a, b) => {
      if (sortBy === 'price-asc') return a.price - b.price;
      if (sortBy === 'price-desc') return b.price - a.price;
      if (sortBy === 'newest') return (b.isNew ? 1 : 0) - (a.isNew ? 1 : 0);
      return (b.tryCount || 0) - (a.tryCount || 0);
    });
  }, [selectedCategory, selectedGender, selectedSize, selectedColor, maxPrice, searchQuery, sortBy]);

  return (
    <div style={{ width: '100%', minHeight: '100vh', backgroundColor: '#fdfcfe', paddingTop: '5.5rem' }}>
      {/* Top Editorial Breadcrumbs & Header */}
      <section style={{ maxWidth: '1280px', margin: '0 auto', padding: '1.5rem 2rem 1rem 2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--vfit-secondary)' }}>
          <span style={{ cursor: 'pointer', color: 'var(--vfit-primary-container)', fontWeight: 600 }} onClick={onNavigateHome}>
            Trang chủ
          </span>
          <span>/</span>
          <span style={{ color: 'var(--vfit-on-surface)', fontWeight: 700 }}>Danh mục sản phẩm</span>
          <span style={{ marginLeft: '0.5rem', backgroundColor: 'var(--vfit-secondary-container)', color: 'var(--vfit-primary-container)', padding: '0.15rem 0.65rem', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 600 }}>
            {filteredProducts.length} mẫu sẵn sàng thử 3D
          </span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', marginTop: '0.75rem', gap: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--vfit-on-surface)', letterSpacing: '-0.03em', margin: 0, textTransform: 'uppercase' }}>
              BỘ SƯU TẬP TRANG PHỤC
            </h1>
            <p style={{ color: 'var(--vfit-secondary)', fontSize: '1rem', marginTop: '0.25rem', maxWidth: '36rem' }}>
              Khám phá và chọn lựa trang phục thời trang cao cấp để thử trực tiếp trên cơ thể 3D của bạn với tỷ lệ chuẩn xác.
            </p>
          </div>

          {/* Quick Search */}
          <div style={{ width: '100%', maxWidth: '320px', position: 'relative' }}>
            <input
              type="text"
              placeholder="Tìm kiếm áo thun, sơ mi, đầm..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="vfit-input-field"
              style={{ height: '2.75rem', paddingLeft: '1rem', paddingRight: '2.5rem', borderRadius: '9999px' }}
            />
            <div style={{ position: 'absolute', right: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--vfit-outline)' }}>
              🔍
            </div>
          </div>
        </div>
      </section>

      {/* Main Layout: Filter Sidebar (Left) + Products Grid (Right) */}
      <div className="vfit-catalog-layout">
        {/* Left Filter Sidebar */}
        <aside className="vfit-filter-sidebar">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', paddingBottom: '0.75rem', borderBottom: '1px solid var(--vfit-surface-container-highest)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 800, color: 'var(--vfit-primary-container)', fontSize: '1rem' }}>
              <span>⚙️</span>
              <span>BỘ LỌC</span>
            </div>
            <button
              type="button"
              onClick={handleResetFilters}
              style={{ background: 'none', border: 'none', color: 'var(--vfit-destructive-crimson)', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer', textDecoration: 'underline' }}
            >
              Xóa bộ lọc
            </button>
          </div>

          {/* 1. Category */}
          <div className="vfit-filter-group">
            <span className="vfit-filter-title">Danh mục</span>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
              {categories.map((cat) => {
                const count =
                  cat.key === 'all'
                    ? MOCK_PRODUCTS.length
                    : MOCK_PRODUCTS.filter((p) => p.category === cat.key).length;
                const isSelected = selectedCategory === cat.key;
                return (
                  <div
                    key={cat.key}
                    onClick={() => setSelectedCategory(cat.key)}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '0.5rem 0.75rem',
                      borderRadius: 'var(--vfit-radius-md)',
                      backgroundColor: isSelected ? 'var(--vfit-primary-container)' : 'transparent',
                      color: isSelected ? '#ffffff' : 'var(--vfit-on-surface)',
                      cursor: 'pointer',
                      fontSize: '0.9rem',
                      fontWeight: isSelected ? 700 : 500,
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <span>{cat.label}</span>
                    <span
                      style={{
                        fontSize: '0.75rem',
                        backgroundColor: isSelected ? 'rgba(255,255,255,0.2)' : 'var(--vfit-surface-container-highest)',
                        padding: '0.1rem 0.5rem',
                        borderRadius: '9999px',
                      }}
                    >
                      {count}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 2. Gender */}
          <div className="vfit-filter-group">
            <span className="vfit-filter-title">Dòng trang phục</span>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.875rem' }}>
              {[
                { key: 'all', label: 'Tất cả' },
                { key: 'womenswear', label: 'Nữ (Womenswear)' },
                { key: 'menswear', label: 'Nam (Menswear)' },
                { key: 'unisex', label: 'Unisex Capsule' },
              ].map((g) => (
                <label
                  key={g.key}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', color: 'var(--vfit-secondary)' }}
                >
                  <input
                    type="radio"
                    name="gender"
                    checked={selectedGender === g.key}
                    onChange={() => setSelectedGender(g.key)}
                    style={{ accentColor: 'var(--vfit-primary-container)' }}
                  />
                  <span style={{ color: selectedGender === g.key ? 'var(--vfit-on-surface)' : 'inherit', fontWeight: selectedGender === g.key ? 700 : 400 }}>
                    {g.label}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* 3. Sizes */}
          <div className="vfit-filter-group">
            <span className="vfit-filter-title">Kích thước (Size)</span>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.4rem' }}>
              <button
                type="button"
                className={`vfit-tab-btn ${selectedSize === 'all' ? 'active' : ''}`}
                style={{ borderRadius: '0.5rem', padding: '0.4rem', fontSize: '0.8rem' }}
                onClick={() => setSelectedSize('all')}
              >
                Tất cả
              </button>
              {sizes.map((s) => (
                <button
                  key={s}
                  type="button"
                  className={`vfit-tab-btn ${selectedSize === s ? 'active' : ''}`}
                  style={{ borderRadius: '0.5rem', padding: '0.4rem', fontSize: '0.8rem' }}
                  onClick={() => setSelectedSize(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* 4. Color Swatches */}
          <div className="vfit-filter-group">
            <span className="vfit-filter-title">Màu sắc</span>
            <div className="vfit-swatch-list">
              {colorSwatches.map((color) => {
                if (color.name === 'all') {
                  return (
                    <button
                      key={color.name}
                      type="button"
                      onClick={() => setSelectedColor('all')}
                      style={{
                        padding: '0.2rem 0.6rem',
                        borderRadius: '9999px',
                        border: '1px solid var(--vfit-outline)',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        backgroundColor: selectedColor === 'all' ? 'var(--vfit-primary-container)' : 'transparent',
                        color: selectedColor === 'all' ? '#ffffff' : 'var(--vfit-secondary)',
                        cursor: 'pointer',
                      }}
                    >
                      Tất cả
                    </button>
                  );
                }
                const isSelected = selectedColor === color.name;
                return (
                  <button
                    key={color.name}
                    type="button"
                    title={color.name}
                    className={`vfit-swatch ${isSelected ? 'active' : ''}`}
                    style={{ backgroundColor: color.hex }}
                    onClick={() => setSelectedColor(color.name)}
                  />
                );
              })}
            </div>
          </div>

          {/* 5. Price Range */}
          <div className="vfit-filter-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="vfit-filter-title">Mức giá tối đa</span>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--vfit-primary-container)' }}>
                {maxPrice.toLocaleString('vi-VN')}₫
              </span>
            </div>
            <input
              type="range"
              min="200000"
              max="2000000"
              step="50000"
              value={maxPrice}
              onChange={(e) => setMaxPrice(Number(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--vfit-primary-container)', cursor: 'pointer' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--vfit-outline)' }}>
              <span>200.000₫</span>
              <span>2.000.000₫</span>
            </div>
          </div>
        </aside>

        {/* Right Product Grid */}
        <main>
          {/* Controls Bar: Results Count & Sort Dropdown */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              backgroundColor: 'var(--vfit-surface-card)',
              padding: '0.85rem 1.25rem',
              borderRadius: 'var(--vfit-radius-lg)',
              boxShadow: '0 2px 8px rgba(8, 10, 97, 0.02)',
              marginBottom: '1.5rem',
              flexWrap: 'wrap',
              gap: '1rem',
            }}
          >
            <div style={{ fontSize: '0.9rem', color: 'var(--vfit-secondary)' }}>
              Hiển thị <strong style={{ color: 'var(--vfit-on-surface)' }}>{filteredProducts.length}</strong> sản phẩm
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--vfit-secondary)' }}>Sắp xếp theo:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                style={{
                  padding: '0.4rem 0.85rem',
                  borderRadius: 'var(--vfit-radius-md)',
                  border: '1px solid var(--vfit-border-subtle)',
                  backgroundColor: 'var(--vfit-surface-container-low)',
                  color: 'var(--vfit-on-surface)',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  outline: 'none',
                  cursor: 'pointer',
                }}
              >
                <option value="popular">Được thử nhiều nhất</option>
                <option value="newest">Mới nhất</option>
                <option value="price-asc">Giá: Thấp đến Cao</option>
                <option value="price-desc">Giá: Cao đến Thấp</option>
              </select>
            </div>
          </div>

          {/* Grid Products */}
          {filteredProducts.length === 0 ? (
            <div
              style={{
                textAlign: 'center',
                padding: '5rem 2rem',
                backgroundColor: 'var(--vfit-surface-card)',
                borderRadius: 'var(--vfit-radius-xl)',
              }}
            >
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>👗</div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--vfit-on-surface)' }}>
                Không tìm thấy trang phục phù hợp
              </h3>
              <p style={{ color: 'var(--vfit-secondary)', fontSize: '0.9rem', margin: '0.5rem 0 1.5rem 0' }}>
                Thử điều chỉnh lại các tiêu chí lọc danh mục, mức giá hoặc kích cỡ của bạn.
              </p>
              <button
                type="button"
                className="vfit-btn-primary"
                style={{ width: 'auto', display: 'inline-flex', padding: '0 1.75rem' }}
                onClick={handleResetFilters}
              >
                Đặt lại bộ lọc
              </button>
            </div>
          ) : (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
                gap: '1.5rem',
              }}
            >
              {filteredProducts.map((product) => (
                <div key={product.id} className="vfit-product-card">
                  {/* Image Thumb */}
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
                        fontSize: '0.7rem',
                        fontWeight: 600,
                        padding: '0.2rem 0.55rem',
                        borderRadius: '9999px',
                      }}
                    >
                      {product.material}
                    </span>

                    {/* Hot / New Badge */}
                    {product.isHot && (
                      <span
                        style={{
                          position: 'absolute',
                          top: '0.75rem',
                          left: '0.75rem',
                          backgroundColor: 'var(--vfit-destructive-crimson)',
                          color: '#ffffff',
                          fontSize: '0.65rem',
                          fontWeight: 700,
                          padding: '0.15rem 0.45rem',
                          borderRadius: '4px',
                        }}
                      >
                        HOT
                      </span>
                    )}

                    {/* Try Count Pill */}
                    {product.tryCount && (
                      <span
                        style={{
                          position: 'absolute',
                          top: '0.75rem',
                          right: '0.75rem',
                          backgroundColor: 'rgba(6, 10, 19, 0.8)',
                          color: '#b6c4ff',
                          fontSize: '0.65rem',
                          fontWeight: 600,
                          padding: '0.15rem 0.5rem',
                          borderRadius: '9999px',
                        }}
                      >
                        ✨ {product.tryCount} lượt thử
                      </span>
                    )}
                  </div>

                  {/* Info */}
                  <div className="vfit-product-info">
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: 'var(--vfit-secondary)', letterSpacing: '0.05em' }}>
                          {product.categoryLabel}
                        </span>
                        <div style={{ display: 'flex', gap: '0.25rem' }}>
                          {product.sizes.map((s) => (
                            <span key={s} style={{ fontSize: '0.65rem', color: 'var(--vfit-outline)' }}>
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>

                      <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--vfit-on-surface)', margin: '0.35rem 0 0.4rem 0', lineHeight: '1.3' }}>
                        {product.name}
                      </h3>

                      <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
                        <span style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--vfit-primary-container)' }}>
                          {product.price.toLocaleString('vi-VN')}₫
                        </span>
                        {product.originalPrice && (
                          <span style={{ fontSize: '0.8rem', color: 'var(--vfit-outline)', textDecoration: 'line-through' }}>
                            {product.originalPrice.toLocaleString('vi-VN')}₫
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Try On Button */}
                    <button
                      type="button"
                      className="vfit-btn-primary"
                      style={{ height: '2.5rem', fontSize: '0.85rem', marginTop: '0.85rem', borderRadius: 'var(--vfit-radius-md)' }}
                      onClick={() => onSelectProductForTryOn(product)}
                    >
                      <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                        <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
                      </svg>
                      <span>THỬ 3D NGAY</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};
