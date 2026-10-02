import React from 'react';
import { useAuth } from '../../hooks/useAuth';

interface NavbarProps {
  currentTab: 'home' | 'catalog' | 'try-on' | 'history' | 'auth';
  onNavigate: (tab: 'home' | 'catalog' | 'try-on' | 'history' | 'auth') => void;
  onOpenTryOn: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, onNavigate, onOpenTryOn }) => {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <header className="vfit-navbar">
      {/* Brand Logo */}
      <div className="vfit-nav-brand" onClick={() => onNavigate('home')}>
        <div className="vfit-brand-logo-icon">V</div>
        <span className="vfit-brand-logo-text">AI TRY-ON</span>
      </div>

      {/* Nav Menu */}
      <nav className="vfit-nav-links">
        <button
          type="button"
          className={`vfit-nav-item ${currentTab === 'home' ? 'active' : ''}`}
          onClick={() => onNavigate('home')}
        >
          Trang chủ
        </button>
        <button
          type="button"
          className={`vfit-nav-item ${currentTab === 'catalog' ? 'active' : ''}`}
          onClick={() => onNavigate('catalog')}
        >
          Sản phẩm
        </button>
        <button
          type="button"
          className={`vfit-nav-item ${currentTab === 'try-on' ? 'active' : ''}`}
          onClick={() => onNavigate('try-on')}
        >
          Phòng thử đồ 3D
        </button>
        <button
          type="button"
          className={`vfit-nav-item ${currentTab === 'history' ? 'active' : ''}`}
          onClick={() => onNavigate('history')}
        >
          Lịch sử thử
        </button>
      </nav>

      {/* Actions */}
      <div className="vfit-nav-actions">
        {/* Wishlist */}
        <button
          type="button"
          className="vfit-icon-btn"
          title="Danh sách yêu thích"
          aria-label="Wishlist"
        >
          <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
          </svg>
          <span className="vfit-badge-count">3</span>
        </button>

        {/* Start Try-On Primary Button */}
        <button
          type="button"
          className="vfit-btn-primary"
          style={{ height: '2.65rem', padding: '0 1.25rem', marginTop: 0, fontSize: '0.85rem' }}
          onClick={onOpenTryOn}
        >
          <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
          </svg>
          <span>THỬ ĐỒ NGAY</span>
        </button>

        {/* Auth profile avatar or login trigger */}
        {isAuthenticated && user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <img
              src={user.avatarUrl}
              alt={user.name}
              title={`${user.name} (${user.email})`}
              style={{
                width: '2.25rem',
                height: '2.25rem',
                borderRadius: '50%',
                border: '2px solid var(--vfit-focus-ring)',
                cursor: 'pointer',
              }}
            />
            <button
              type="button"
              onClick={logout}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--vfit-destructive-crimson)',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Thoát
            </button>
          </div>
        ) : (
          <button
            type="button"
            className="vfit-btn-secondary"
            style={{ height: '2.65rem', padding: '0 1rem', fontSize: '0.85rem' }}
            onClick={() => onNavigate('auth')}
          >
            Đăng nhập
          </button>
        )}
      </div>
    </header>
  );
};
