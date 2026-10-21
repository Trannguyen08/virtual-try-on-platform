import React from 'react';
import { FeaturedProductsSection } from '../../components/home/FeaturedProductsSection';
import { HeroSection } from '../../components/home/HeroSection';
import { HowItWorksSection } from '../../components/home/HowItWorksSection';
import { Product } from '../../data/mockProducts';

interface HomePageProps {
  onStartTryOn: () => void;
  onExploreCatalog: () => void;
  onSelectProductForTryOn: (product: Product) => void;
  onViewProductDetail?: (product: Product) => void;
}

export const HomePage: React.FC<HomePageProps> = ({
  onStartTryOn,
  onExploreCatalog,
  onSelectProductForTryOn,
  onViewProductDetail,
}) => {
  return (
    <div style={{ width: '100%' }}>
      {/* 1. Hero Section */}
      <HeroSection
        onStartTryOn={onStartTryOn}
        onExploreCatalog={onExploreCatalog}
      />

      {/* 2. How It Works (Bento Grid) */}
      <HowItWorksSection />

      {/* 3. Featured Products Lookbook */}
      <FeaturedProductsSection
        onSelectProductForTryOn={onSelectProductForTryOn}
        onViewProductDetail={onViewProductDetail}
        onViewAllCatalog={onExploreCatalog}
      />

      {/* 4. Bottom CTA Showcase Banner */}
      <section style={{ maxWidth: '1280px', margin: '2rem auto 5rem auto', padding: '0 2rem' }}>
        <div
          style={{
            background: 'linear-gradient(135deg, var(--vfit-primary-container) 0%, var(--vfit-dark-primary) 100%)',
            borderRadius: 'var(--vfit-radius-xl)',
            padding: '3.5rem 2.5rem',
            color: '#ffffff',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '2rem',
            boxShadow: '0 20px 40px -10px rgba(8, 10, 97, 0.35)',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {/* Subtle neon glow circles inside banner */}
          <div
            style={{
              position: 'absolute',
              top: '-5rem',
              right: '-5rem',
              width: '18rem',
              height: '18rem',
              borderRadius: '50%',
              backgroundColor: 'rgba(61, 126, 255, 0.35)',
              filter: 'blur(50px)',
              pointerEvents: 'none',
            }}
          />

          <div style={{ maxWidth: '600px', zIndex: 1 }}>
            <span
              style={{
                fontSize: '0.75rem',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                backgroundColor: 'rgba(255, 255, 255, 0.15)',
                padding: '0.35rem 0.85rem',
                borderRadius: '9999px',
                display: 'inline-block',
                marginBottom: '1rem',
              }}
            >
              Phòng Thử Đồ Cá Nhân 3D
            </span>
            <h2 style={{ fontSize: '2.4rem', fontWeight: 800, margin: '0 0 1rem 0', letterSpacing: '-0.025em', lineHeight: '1.2' }}>
              Sẵn sàng định hình phong cách cùng AI Try-On?
            </h2>
            <p style={{ color: '#cbd5e1', fontSize: '1.05rem', lineHeight: '1.6', margin: 0 }}>
              Không còn nỗi lo mua sắm sai size hoặc quần áo không hợp dáng. Thử nghiệm tức thì ngay trên thiết bị của bạn hoàn toàn miễn phí.
            </p>
          </div>

          <div style={{ zIndex: 1 }}>
            <button
              type="button"
              className="vfit-btn-primary"
              style={{
                backgroundColor: '#ffffff',
                color: 'var(--vfit-primary-container)',
                height: '3.5rem',
                padding: '0 2.25rem',
                fontSize: '1rem',
                boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)',
              }}
              onClick={onStartTryOn}
            >
              <span>TRẢI NGHIỆM NGAY</span>
              <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};
