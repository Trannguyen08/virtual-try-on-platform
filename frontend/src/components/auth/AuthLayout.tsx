import React from 'react';

interface AuthLayoutProps {
  children: React.ReactNode;
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  return (
    <div className="vfit-auth-wrapper">
      {/* Subtle Ambient Glows and Tech Grid Accents */}
      <div className="vfit-ambient-glow-1" />
      <div className="vfit-ambient-glow-2" />

      <div style={{ width: '100%', maxWidth: '480px', position: 'relative', zIndex: 10 }}>
        {/* Main Authentication Card */}
        <div className="vfit-auth-card">
          {/* Decorative Atmospheric Scan Line */}
          <div className="vfit-scan-line" />

          {children}

          {/* AI & Encryption Trust Badge */}
          <div className="vfit-trust-badge">
            <svg
              className="vfit-trust-icon"
              width="16"
              height="16"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
            >
              <rect height="11" rx="2" ry="2" width="18" x="3" y="11" />
              <path d="M7 11V7a5 5 0 0110 0v4" />
            </svg>
            <span>Dữ liệu khuôn mặt và vóc dáng được mã hóa bảo mật 256-bit</span>
          </div>
        </div>

        {/* Editorial Micro-Footer */}
        <div className="vfit-micro-footer">
          <a href="#terms">Điều khoản dịch vụ</a>
          <span>•</span>
          <a href="#policy">Chính sách AI Studio</a>
          <span>•</span>
          <a href="#help">Trợ giúp</a>
        </div>
      </div>
    </div>
  );
};
