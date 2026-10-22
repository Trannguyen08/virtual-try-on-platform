import React from 'react';

interface ProcessingStepProps {
  statusMessage: string;
}

export const ProcessingStep: React.FC<ProcessingStepProps> = ({ statusMessage }) => {
  return (
    <div
      style={{
        maxWidth: '650px',
        margin: '2rem auto',
        textAlign: 'center',
        backgroundColor: 'var(--vfit-surface-card)',
        borderRadius: 'var(--vfit-radius-xl)',
        padding: '3rem 2rem',
        boxShadow: '0 4px 25px rgba(8, 10, 97, 0.06)',
      }}
    >
      {/* Radar Scanner Animation */}
      <div className="vfit-radar-scanner">
        <div className="vfit-radar-pulse" aria-hidden="true" />
      </div>

      <span
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.4rem',
          padding: '0.25rem 0.75rem',
          borderRadius: '9999px',
          backgroundColor: 'var(--vfit-secondary-container)',
          color: 'var(--vfit-primary-container)',
          fontSize: '0.75rem',
          fontWeight: 700,
          textTransform: 'uppercase',
          marginBottom: '0.75rem',
        }}
      >
        <span className="vfit-pulse-dot" />
        Đang chuẩn bị mô hình 3D
      </span>

      <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--vfit-on-surface)', margin: '0 0 0.5rem 0' }}>
        ĐANG KHỞI TẠO PHÒNG THỬ ĐỒ ẢO
      </h2>

      <p style={{ color: 'var(--vfit-secondary)', fontSize: '0.95rem', minHeight: '1.5rem', margin: '0.5rem 0 1.5rem 0', fontWeight: 600 }}>
        {statusMessage || 'Đang chờ kết quả xử lý...'}
      </p>

      {/* Indeterminate activity indicator; Blender does not report a percentage. */}
      <div style={{ width: '100%', height: '8px', backgroundColor: 'var(--vfit-surface-container-high)', borderRadius: '9999px', overflow: 'hidden', margin: '0 auto 1.5rem auto' }}>
        <div
          style={{
            width: '35%',
            height: '100%',
            background: 'linear-gradient(90deg, var(--vfit-primary-container) 0%, var(--vfit-focus-ring) 100%)',
            borderRadius: '9999px',
            animation: 'vfit-processing-indeterminate 1.5s ease-in-out infinite alternate',
          }}
        />
      </div>

      {/* Subtext info */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', color: 'var(--vfit-outline)', fontSize: '0.8rem' }}>
        <span>Đang xử lý</span>
        <span>•</span>
        <span>Đồ họa 3D</span>
        <span>•</span>
        <span>Bản xem thử 3D</span>
      </div>
    </div>
  );
};
