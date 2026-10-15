import React, { Suspense, useEffect, useState } from 'react';
import { Footer } from './components/common/Footer';
import { AppTab, Navbar } from './components/common/Navbar';
import { AuthProvider } from './context/AuthContext';
import { Product } from './data/mockProducts';
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { CatalogPage } from './pages/catalog/CatalogPage';
import { HomePage } from './pages/home/HomePage';
import { TryOnPage } from './pages/tryon/TryOnPage';
import './styles/auth.css';
import './styles/home.css';
import './styles/tryon.css';
import './styles/garment3d.css';

const Garment3DPage = React.lazy(() => import('./pages/Garment3DPage'));

const TAB_PATHS: Record<AppTab, string> = {
  home: '/',
  catalog: '/catalog',
  'try-on': '/try-on',
  'garment-3d': '/garment-3d',
  history: '/history',
  auth: '/auth',
};

const tabFromPath = (): AppTab => {
  if (window.location.pathname === '/garment3d.html') return 'garment-3d';
  const entry = (Object.entries(TAB_PATHS) as [AppTab, string][])
    .find(([, path]) => path === window.location.pathname);
  return entry?.[0] ?? 'home';
};

const MainContent: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<AppTab>(tabFromPath);
  const [authView, setAuthView] = useState<'login' | 'register'>('login');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  useEffect(() => {
    if (window.location.pathname === '/garment3d.html') {
      window.history.replaceState(null, '', TAB_PATHS['garment-3d']);
    }
    const onPopState = () => setCurrentTab(tabFromPath());
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  const navigate = (tab: AppTab) => {
    setCurrentTab(tab);
    const path = TAB_PATHS[tab];
    if (window.location.pathname !== path) window.history.pushState(null, '', path);
    window.scrollTo({ top: 0, behavior: 'auto' });
  };

  const handleSelectProductForTryOn = (product: Product) => {
    setSelectedProduct(product);
    navigate('try-on');
  };

  
  const handleStartTryOn = () => {
    setSelectedProduct(null);
    navigate('try-on');
  };

  // Nếu người dùng chọn vào trang đăng nhập/đăng ký
  if (currentTab === 'auth') {
    return (
      <div>
        {/* Nút quay lại trang chủ ở góc trên */}
        <div style={{ position: 'fixed', top: '1.25rem', left: '1.25rem', zIndex: 100 }}>
          <button
            type="button"
            onClick={() => navigate('home')}
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
            onLoginSuccess={() => navigate('home')}
          />
        ) : (
          <RegisterPage
            onNavigateToLogin={() => setAuthView('login')}
            onRegisterSuccess={() => navigate('home')}
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
        onNavigate={navigate}
        onOpenTryOn={handleStartTryOn}
      />

      {/* Main Content Area */}
      <main style={{ flex: 1 }}>
        {currentTab === 'home' && (
          <HomePage
            onStartTryOn={handleStartTryOn}
            onExploreCatalog={() => navigate('catalog')}
            onSelectProductForTryOn={handleSelectProductForTryOn}
          />
        )}

        {currentTab === 'catalog' && (
          <CatalogPage
            onNavigateHome={() => navigate('home')}
            onSelectProductForTryOn={handleSelectProductForTryOn}
          />
        )}

        {currentTab === 'try-on' && (
          <div style={{ paddingTop: '5rem', maxWidth: '1440px', margin: '0 auto', padding: '5.5rem 1.5rem 3rem 1.5rem' }}>
            <TryOnPage
              initialGarment={selectedProduct}
              onNavigateCatalog={() => navigate('catalog')}
            />
          </div>
        )}

        {currentTab === 'garment-3d' && (
          <div className="vfit-garment-page">
            <Suspense fallback={<p className="vfit-garment-loading" role="status">Đang mở trang tạo trang phục 3D…</p>}>
              <Garment3DPage />
            </Suspense>
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
