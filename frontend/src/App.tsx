import React, { useState } from 'react';
import { UserHeaderProfile } from './components/auth/UserHeaderProfile';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { UploadPage } from './pages/UploadPage';
import './styles/auth.css';

const MainContent: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const [authView, setAuthView] = useState<'login' | 'register'>('login');
  const [isGuestMode, setIsGuestMode] = useState<boolean>(false);

  if (isLoading) {
    return (
      <div className="vfit-auth-wrapper">
        <div className="vfit-spinner" style={{ width: '2.5rem', height: '2.5rem', borderColor: '#080a61', borderTopColor: '#3d7eff' }} />
      </div>
    );
  }

  // Khi đã đăng nhập hoặc chọn chế độ khách (Guest)
  if (isAuthenticated || isGuestMode) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#fdfcfe' }}>
        {isAuthenticated && <UserHeaderProfile onStartTryOn={() => setIsGuestMode(false)} />}
        {isGuestMode && !isAuthenticated && (
          <div
            style={{
              padding: '0.65rem 1.5rem',
              backgroundColor: '#dae3f5',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              fontSize: '0.875rem',
            }}
          >
            <span>Đang ở chế độ dùng thử khách (Guest)</span>
            <button
              type="button"
              className="vfit-link"
              onClick={() => setIsGuestMode(false)}
            >
              Đăng nhập để lưu lịch sử
            </button>
          </div>
        )}
        <main style={{ flex: 1, padding: '1.5rem' }}>
          <UploadPage />
        </main>
      </div>
    );
  }

  // Khi chưa đăng nhập: Hiển thị màn hình Login / Register
  return (
    <div>
      {authView === 'login' ? (
        <LoginPage
          onNavigateToRegister={() => setAuthView('register')}
          onLoginSuccess={() => {}}
        />
      ) : (
        <RegisterPage
          onNavigateToLogin={() => setAuthView('login')}
          onRegisterSuccess={() => {}}
        />
      )}

      {/* Tùy chọn trải nghiệm nhanh không cần đăng nhập */}
      <div
        style={{
          position: 'fixed',
          bottom: '1rem',
          right: '1rem',
          zIndex: 20,
        }}
      >
        <button
          type="button"
          onClick={() => setIsGuestMode(true)}
          style={{
            background: 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(8px)',
            border: '1px solid #dae3f5',
            borderRadius: '9999px',
            padding: '0.5rem 1rem',
            fontSize: '0.8rem',
            fontWeight: 600,
            color: '#080a61',
            boxShadow: '0 4px 12px rgba(8, 10, 97, 0.08)',
            cursor: 'pointer',
          }}
        >
          Dùng thử không cần đăng nhập →
        </button>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <MainContent />
    </AuthProvider>
  );
};

export default App;
