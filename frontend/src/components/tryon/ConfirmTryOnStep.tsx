import React, { useState } from 'react';
import { Product } from '../../data/mockProducts';
import { BodyCustomParams, BODY_PRESETS } from '../../data/bodyPresets';

interface ConfirmTryOnStepProps {
  photoPreview: string;
  heightCm: number;
  garment: Product;
  selectedSize: string;
  customParams?: BodyCustomParams;
  onBack: () => void;
  onChangeModel: () => void;
  onChangeGarment: () => void;
  onConfirmStart: () => void;
}

export const ConfirmTryOnStep: React.FC<ConfirmTryOnStepProps> = ({
  photoPreview,
  heightCm,
  garment,
  selectedSize,
  customParams,
  onBack,
  onChangeModel,
  onChangeGarment,
  onConfirmStart,
}) => {
  const [agreedConsent, setAgreedConsent] = useState(true);
  const [modelAngle, setModelAngle] = useState<'front' | 'side' | 'back'>('front');

  const selectedPreset = BODY_PRESETS.find((p) => p.id === customParams?.selectedPresetId);

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header & Subtitle */}
      <div style={{ textAlign: 'center', maxWidth: '700px', margin: '0 auto' }}>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.3rem 0.85rem',
            borderRadius: '9999px',
            backgroundColor: 'var(--vfit-secondary-container)',
            color: 'var(--vfit-primary-container)',
            fontSize: '0.75rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
            marginBottom: '0.5rem',
          }}
        >
          <span>✨ NEURAL DRAPING PRE-FLIGHT</span>
        </div>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--vfit-on-surface)', margin: '0 0 0.5rem 0', letterSpacing: '-0.02em' }}>
          XÁC NHẬN CẤU HÌNH THỬ ĐỒ ẢO
        </h1>
        <p style={{ color: 'var(--vfit-secondary)', fontSize: '0.95rem', margin: 0, lineHeight: 1.5 }}>
          Kiểm tra lại hình ảnh chân dung và trang phục bạn đã chọn trước khi AI xử lý mô phỏng chuyển động 3D chuẩn xác.
        </p>
      </div>

      {/* Dual Preview & AI Pairing Canvas */}
      <div
        style={{
          position: 'relative',
          backgroundColor: '#fff',
          borderRadius: 'var(--vfit-radius-xl)',
          padding: '1.75rem',
          boxShadow: '0 4px 20px rgba(8, 10, 97, 0.05)',
          border: '1px solid var(--vfit-border-subtle)',
        }}
      >
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem', position: 'relative' }}>
          {/* Column Left: Model Canvas */}
          <div
            style={{
              backgroundColor: 'var(--vfit-surface-card)',
              borderRadius: 'var(--vfit-radius-lg)',
              padding: '1.25rem',
              border: '1px solid var(--vfit-border-subtle)',
              boxShadow: '0 2px 10px rgba(8, 10, 97, 0.03)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <span style={{ fontSize: '1.1rem' }}>👤</span>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--vfit-on-surface)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  ẢNH NGƯỜI MẪU CỦA BẠN
                </span>
              </div>
              <button
                type="button"
                onClick={onChangeModel}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--vfit-focus-ring)',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.2rem',
                }}
              >
                Đổi ảnh khác
              </button>
            </div>

            {/* Model Image Preview */}
            <div
              style={{
                position: 'relative',
                aspectRatio: '3 / 4',
                maxHeight: '440px',
                borderRadius: 'var(--vfit-radius-md)',
                overflow: 'hidden',
                backgroundColor: 'var(--vfit-surface-container-low)',
              }}
            >
              <img
                src={photoPreview}
                alt="Người mẫu"
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />

              {/* Tag Overlay */}
              <div
                style={{
                  position: 'absolute',
                  top: '0.75rem',
                  left: '0.75rem',
                  backgroundColor: 'rgba(8, 10, 97, 0.85)',
                  backdropFilter: 'blur(6px)',
                  color: '#fff',
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  padding: '0.3rem 0.65rem',
                  borderRadius: '9999px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                }}
              >
                <div className="vfit-pulse-dot" />
                <span>Phân tích cơ thể hợp lệ</span>
              </div>

              {/* Angle Switcher */}
              <div
                style={{
                  position: 'absolute',
                  bottom: '0.75rem',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  backgroundColor: 'rgba(255, 255, 255, 0.9)',
                  backdropFilter: 'blur(8px)',
                  padding: '0.25rem 0.5rem',
                  borderRadius: '9999px',
                  display: 'flex',
                  gap: '0.25rem',
                  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                }}
              >
                {(['front', 'side', 'back'] as const).map((angle) => (
                  <button
                    key={angle}
                    type="button"
                    onClick={() => setModelAngle(angle)}
                    style={{
                      border: 'none',
                      backgroundColor: modelAngle === angle ? 'var(--vfit-primary-container)' : 'transparent',
                      color: modelAngle === angle ? '#fff' : 'var(--vfit-secondary)',
                      fontSize: '0.7rem',
                      fontWeight: 600,
                      padding: '0.2rem 0.5rem',
                      borderRadius: '9999px',
                      cursor: 'pointer',
                    }}
                  >
                    {angle === 'front' ? 'Chính diện' : angle === 'side' ? 'Góc nghiêng 45°' : 'Sau lưng'}
                  </button>
                ))}
              </div>
            </div>

            {/* Model Metadata Tags */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginTop: '0.85rem' }}>
              <span style={{ fontSize: '0.75rem', padding: '0.25rem 0.65rem', borderRadius: '9999px', backgroundColor: 'var(--vfit-surface-container)', color: 'var(--vfit-primary-container)', fontWeight: 700 }}>
                🧬 {selectedPreset ? selectedPreset.name : '3D Custom Biometrics'}
              </span>
              <span style={{ fontSize: '0.75rem', padding: '0.25rem 0.65rem', borderRadius: '9999px', backgroundColor: 'var(--vfit-surface-container)', color: 'var(--vfit-on-surface)' }}>
                Cao: {heightCm} cm • {customParams?.weight || 50}kg
              </span>
              {customParams && (
                <span style={{ fontSize: '0.75rem', padding: '0.25rem 0.65rem', borderRadius: '9999px', backgroundColor: 'var(--vfit-surface-container)', color: 'var(--vfit-secondary)' }}>
                  Vai {Math.round(customParams.proportions.shoulder_width * 100)}% • Eo {Math.round(customParams.proportions.waist * 100)}% • Hông {Math.round(customParams.proportions.hips * 100)}%
                </span>
              )}
              <span style={{ fontSize: '0.75rem', padding: '0.25rem 0.65rem', borderRadius: '9999px', backgroundColor: 'var(--vfit-surface-container)', color: 'var(--vfit-focus-ring)', fontWeight: 600 }}>
                ⚡ Mesh: {customParams?.glbModelUrl?.split('/').pop() || 'body_default.glb'}
              </span>
            </div>
          </div>

          {/* Center AI Neural Connector Node */}
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              zIndex: 10,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              pointerEvents: 'none',
            }}
          >
            <div
              style={{
                width: '3.75rem',
                height: '3.75rem',
                borderRadius: '50%',
                backgroundColor: 'var(--vfit-primary-container)',
                color: '#fff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 6px 20px rgba(8, 10, 97, 0.4)',
                border: '4px solid #fff',
                fontSize: '1.5rem',
              }}
            >
              ⚡
            </div>
            <div
              style={{
                marginTop: '0.35rem',
                padding: '0.2rem 0.65rem',
                backgroundColor: '#fff',
                borderRadius: '9999px',
                fontSize: '0.65rem',
                fontWeight: 800,
                color: 'var(--vfit-primary-container)',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              AI Neural Fitting
            </div>
          </div>

          {/* Column Right: Garment Canvas */}
          <div
            style={{
              backgroundColor: 'var(--vfit-surface-card)',
              borderRadius: 'var(--vfit-radius-lg)',
              padding: '1.25rem',
              border: '1px solid var(--vfit-border-subtle)',
              boxShadow: '0 2px 10px rgba(8, 10, 97, 0.03)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <span style={{ fontSize: '1.1rem' }}>👗</span>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--vfit-on-surface)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  TRANG PHỤC ĐÃ CHỌN
                </span>
              </div>
              <button
                type="button"
                onClick={onChangeGarment}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--vfit-focus-ring)',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.2rem',
                }}
              >
                Chọn mẫu khác
              </button>
            </div>

            {/* Garment Image Preview */}
            <div
              style={{
                position: 'relative',
                aspectRatio: '3 / 4',
                maxHeight: '440px',
                borderRadius: 'var(--vfit-radius-md)',
                overflow: 'hidden',
                backgroundColor: 'var(--vfit-surface-container-low)',
              }}
            >
              <img
                src={garment.imageUrl}
                alt={garment.name}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />

              {/* Fit Accuracy Gauge */}
              <div
                style={{
                  position: 'absolute',
                  top: '0.75rem',
                  right: '0.75rem',
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  backdropFilter: 'blur(6px)',
                  color: 'var(--vfit-primary-container)',
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  padding: '0.3rem 0.65rem',
                  borderRadius: '9999px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.3rem',
                  boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
                }}
              >
                <span>✓</span>
                <span>99.4% Chuẩn form vải</span>
              </div>

              <div
                style={{
                  position: 'absolute',
                  bottom: '0.75rem',
                  left: '0.75rem',
                  backgroundColor: 'var(--vfit-primary-container)',
                  color: '#fff',
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  padding: '0.3rem 0.65rem',
                  borderRadius: '9999px',
                }}
              >
                {garment.tagline}
              </div>
            </div>

            {/* Garment Info Box */}
            <div style={{ marginTop: '0.85rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                <div>
                  <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 800, color: 'var(--vfit-on-surface)' }}>
                    {garment.name}
                  </h3>
                  <span style={{ fontSize: '0.75rem', color: 'var(--vfit-secondary)' }}>
                    Chất liệu: {garment.material}
                  </span>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--vfit-primary-container)' }}>
                    {garment.price.toLocaleString('vi-VN')}₫
                  </span>
                </div>
              </div>

              {/* Specs Badges */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginTop: '0.75rem' }}>
                <div style={{ padding: '0.5rem 0.75rem', backgroundColor: 'var(--vfit-surface-container-low)', borderRadius: 'var(--vfit-radius-md)' }}>
                  <span style={{ fontSize: '0.65rem', color: 'var(--vfit-secondary)', textTransform: 'uppercase' }}>Màu sắc</span>
                  <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--vfit-on-surface)' }}>
                    {garment.colors[0]?.name || 'Mặc định'}
                  </div>
                </div>

                <div style={{ padding: '0.5rem 0.75rem', backgroundColor: 'var(--vfit-surface-container-low)', borderRadius: 'var(--vfit-radius-md)' }}>
                  <span style={{ fontSize: '0.65rem', color: 'var(--vfit-secondary)', textTransform: 'uppercase' }}>Kích thước</span>
                  <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--vfit-primary-container)' }}>
                    Size {selectedSize} (Khuyên dùng)
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Simulation Settings Summary Card */}
      <div
        style={{
          backgroundColor: '#fff',
          borderRadius: 'var(--vfit-radius-xl)',
          padding: '1.25rem 1.75rem',
          border: '1px solid var(--vfit-border-subtle)',
          boxShadow: '0 2px 8px rgba(8, 10, 97, 0.03)',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div
            style={{
              width: '2.5rem',
              height: '2.5rem',
              borderRadius: '50%',
              backgroundColor: 'var(--vfit-secondary-container)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--vfit-primary-container)',
              fontSize: '1.2rem',
            }}
          >
            ⚙️
          </div>
          <div>
            <h4 style={{ margin: 0, fontSize: '0.9rem', fontWeight: 700, color: 'var(--vfit-on-surface)' }}>
              Thông số môi trường kết xuất AI
            </h4>
            <span style={{ fontSize: '0.75rem', color: 'var(--vfit-secondary)' }}>
              Hệ thống tự động tính toán ma trận lực rủ, nếp gấp vải và bóng quang sai thực
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          <span style={{ fontSize: '0.75rem', padding: '0.3rem 0.75rem', borderRadius: '9999px', backgroundColor: 'var(--vfit-secondary-container)', color: 'var(--vfit-primary-container)', fontWeight: 700 }}>
            3D Engine: <strong>Blender MPFB + WebGL</strong>
          </span>
          <span style={{ fontSize: '0.75rem', padding: '0.3rem 0.75rem', borderRadius: '9999px', backgroundColor: 'var(--vfit-surface-container)', color: 'var(--vfit-on-surface)' }}>
            Render: <strong>~3.5 giây</strong>
          </span>
          <span style={{ fontSize: '0.75rem', padding: '0.3rem 0.75rem', borderRadius: '9999px', backgroundColor: 'var(--vfit-surface-container)', color: 'var(--vfit-on-surface)' }}>
            Độ phân giải: <strong>Ultra-HD 4K Ray-traced</strong>
          </span>
          <span style={{ fontSize: '0.75rem', padding: '0.3rem 0.75rem', borderRadius: '9999px', backgroundColor: 'var(--vfit-surface-container)', color: 'var(--vfit-on-surface)' }}>
            Thuật toán: <strong>Cloth Physics 4.2</strong>
          </span>
        </div>
      </div>

      {/* Consent & Bottom Floating Action Bar */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.8rem', color: 'var(--vfit-secondary)', maxWidth: '650px', textAlign: 'center' }}>
          <input
            type="checkbox"
            checked={agreedConsent}
            onChange={(e) => setAgreedConsent(e.target.checked)}
            style={{ accentColor: 'var(--vfit-primary-container)', cursor: 'pointer' }}
          />
          <span>
            Tôi đồng ý cho hệ thống xử lý hình ảnh và dữ liệu sinh trắc học để tạo kết quả thử đồ cá nhân hóa (Bảo mật e2ee, tự động xóa sau 24h).
          </span>
        </label>

        <div style={{ display: 'flex', gap: '1rem', width: '100%', maxWidth: '520px' }}>
          <button
            type="button"
            className="vfit-btn-secondary"
            onClick={onBack}
            style={{ flex: 1, height: '3.25rem', justifyContent: 'center' }}
          >
            ← Quay lại chọn đồ
          </button>

          <button
            type="button"
            className="vfit-btn-primary"
            disabled={!agreedConsent}
            onClick={onConfirmStart}
            style={{ flex: 2, height: '3.25rem', justifyContent: 'center', opacity: agreedConsent ? 1 : 0.6 }}
          >
            <span style={{ fontSize: '1.1rem' }}>🪄</span>
            <span style={{ letterSpacing: '0.04em' }}>BẮT ĐẦU TẠO ẢNH THỬ ĐỒ</span>
            <span>→</span>
          </button>
        </div>

        <div style={{ fontSize: '0.75rem', color: 'var(--vfit-outline)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <span>🔒</span> Cam kết bảo mật dữ liệu sinh trắc học chuẩn GDPR & CCPA
        </div>
      </div>
    </div>
  );
};
