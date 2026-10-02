import React, { useEffect, useState } from 'react';

interface ProcessingStepProps {
  statusMessage: string;
}

export const ProcessingStep: React.FC<ProcessingStepProps> = ({ statusMessage }) => {
  const [progress, setProgress] = useState(15);

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prev) => (prev < 90 ? prev + 12 : prev));
    }, 400);
    return () => clearInterval(timer);
  }, []);

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
        <div className="vfit-radar-pulse">🪄</div>
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
        AI Engine Đang Xử Lý 3D Realtime
      </span>

      <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--vfit-on-surface)', margin: '0 0 0.5rem 0' }}>
        ĐANG KHỞI TẠO PHÒNG THỬ ĐỒ ẢO
      </h2>

      <p style={{ color: 'var(--vfit-secondary)', fontSize: '0.95rem', minHeight: '1.5rem', margin: '0.5rem 0 1.5rem 0', fontWeight: 600 }}>
        {statusMessage || 'Đang quét vóc dáng và khớp mô hình vải...'}
      </p>

      {/* Progress Bar */}
      <div style={{ width: '100%', height: '8px', backgroundColor: 'var(--vfit-surface-container-high)', borderRadius: '9999px', overflow: 'hidden', margin: '0 auto 1.5rem auto' }}>
        <div
          style={{
            width: `${progress}%`,
            height: '100%',
            background: 'linear-gradient(90deg, var(--vfit-primary-container) 0%, var(--vfit-focus-ring) 100%)',
            borderRadius: '9999px',
            transition: 'width 0.4s ease',
          }}
        />
      </div>

      {/* Subtext info */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', color: 'var(--vfit-outline)', fontSize: '0.8rem' }}>
        <span>⚡ SMPL-X Biometrics</span>
        <span>•</span>
        <span>🌐 Three.js WebGL</span>
        <span>•</span>
        <span>📐 Chuẩn xác 99.4%</span>
      </div>
    </div>
  );
};
