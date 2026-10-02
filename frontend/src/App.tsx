import React, { useState } from 'react';
import { Footer } from './components/common/Footer';
import { Navbar } from './components/common/Navbar';
import { AuthProvider } from './context/AuthContext';
import { Product } from './data/mockProducts';
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { CatalogPage } from './pages/catalog/CatalogPage';
import { HomePage } from './pages/home/HomePage';
import { UploadPage } from './pages/UploadPage';
import './styles/auth.css';
import './styles/home.css';

type AppTab = 'home' | 'catalog' | 'try-on' | 'history' | 'auth';

const MainContent: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<AppTab>('home');
  const [authView, setAuthView] = useState<'login' | 'register'>('login');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  const handleSelectProductForTryOn = (product: Product) => {
    setSelectedProduct(product);
    setCurrentTab('try-on');
  };

  const handleStartTryOn = () => {
    setSelectedProduct(null);
    setCurrentTab('try-on');
  };

  // Nếu người dùng chọn vào trang đăng nhập/đăng ký
  if (currentTab === 'auth') {
    return (
      <div>
        {/* Nút quay lại trang chủ ở góc trên */}
        <div style={{ position: 'fixed', top: '1.25rem', left: '1.25rem', zIndex: 100 }}>
          <button
            type="button"
            onClick={() => setCurrentTab('home')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              backdropFilter: 'blur(8px)',
              border: '1px solid var(--vfit-border-subtle)',
              padding: '0.5rem 1rem',
              borderRadius: '9999px',
              fontSize: '0.85rem',
              fontWeight: 600,
              color: 'var(--vfit-primary-container)',
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(8, 10, 97, 0.08)',
            }}
          >
            ← Quay lại trang chủ
          </button>
        </div>

        {authView === 'login' ? (
          <LoginPage
            onNavigateToRegister={() => setAuthView('register')}
            onLoginSuccess={() => setCurrentTab('home')}
          />
        ) : (
          <RegisterPage
            onNavigateToLogin={() => setAuthView('login')}
            onRegisterSuccess={() => setCurrentTab('home')}
          />
        )}
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#fdfcfe' }}>
      {/* Persistent Global Header */}
      <Navbar
        currentTab={currentTab}
        onNavigate={(tab) => setCurrentTab(tab)}
        onOpenTryOn={handleStartTryOn}
      />

      {/* Main Content Area */}
      <main style={{ flex: 1 }}>
        {currentTab === 'home' && (
          <HomePage
            onStartTryOn={handleStartTryOn}
            onExploreCatalog={() => setCurrentTab('catalog')}
            onSelectProductForTryOn={handleSelectProductForTryOn}
          />
        )}

        {currentTab === 'catalog' && (
          <CatalogPage
            onNavigateHome={() => setCurrentTab('home')}
            onSelectProductForTryOn={handleSelectProductForTryOn}
          />
        )}

        {currentTab === 'try-on' && (
          <div style={{ paddingTop: '5.5rem', maxWidth: '1280px', margin: '0 auto', padding: '6rem 2rem 3rem 2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <h1 style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--vfit-on-surface)', margin: 0 }}>
                  PHÒNG THỬ ĐỒ ẢO 3D
                </h1>
                <p style={{ color: 'var(--vfit-secondary)', fontSize: '0.95rem', margin: '0.35rem 0 0 0' }}>
                  {selectedProduct
                    ? `Đang chọn thử mẫu: ${selectedProduct.name} (${selectedProduct.categoryLabel})`
                    : 'Tải ảnh của bạn để AI tái tạo mô hình 3D và thử trang phục'}
                </p>
              </div>

              <button
                type="button"
                className="vfit-btn-secondary"
                style={{ height: '2.5rem', fontSize: '0.85rem' }}
                onClick={() => setCurrentTab('catalog')}
              >
                ← Chọn trang phục khác
              </button>
            </div>

            {/* Upload & 3D Try-On Component */}
            <div style={{ backgroundColor: 'var(--vfit-surface-card)', borderRadius: 'var(--vfit-radius-xl)', padding: '2rem', boxShadow: '0 4px 20px rgba(8, 10, 97, 0.05)' }}>
              <UploadPage />
            </div>
          </div>
        )}

        {currentTab === 'history' && (
          <div style={{ paddingTop: '6rem', maxWidth: '1280px', margin: '0 auto', padding: '6rem 2rem 4rem 2rem', textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🕰️</div>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--vfit-on-surface)' }}>
              LỊCH SỬ THỬ ĐỒ 3D
            </h2>
            <p style={{ color: 'var(--vfit-secondary)', maxWidth: '400px', margin: '0.5rem auto 1.5rem auto' }}>
              Bạn chưa có lần thử đồ nào được lưu. Hãy bắt đầu chọn một bộ trang phục yêu thích để thử ngay!
            </p>
            <button
              type="button"
              className="vfit-btn-primary"
              style={{ width: 'auto', display: 'inline-flex', padding: '0 2rem' }}
              onClick={handleStartTryOn}
            >
              THỬ ĐỒ NGAY
            </button>
          </div>
        )}
      </main>

      {/* Global Footer */}
      <Footer />
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
