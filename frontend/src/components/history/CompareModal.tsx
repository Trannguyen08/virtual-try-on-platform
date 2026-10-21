import React, { useState, useRef } from 'react';
import { TryOnHistoryItem } from '../../data/mockHistory';

interface CompareModalProps {
  item: TryOnHistoryItem;
  onClose: () => void;
  onReTry: (item: TryOnHistoryItem) => void;
}

export const CompareModal: React.FC<CompareModalProps> = ({ item, onClose, onReTry }) => {
  const [sliderPosition, setSliderPosition] = useState<number>(50); // percentage 0 - 100
  const containerRef = useRef<HTMLDivElement>(null);

  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percent = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPosition(percent);
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = item.resultPhotoUrl;
    link.download = `VFit-AI-TryOn-${item.productName.replace(/\s+/g, '-')}.jpg`;
    link.target = '_blank';
    link.click();
  };

  return (
    <div className="vfit-modal-backdrop" onClick={onClose}>
      <div className="vfit-modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="vfit-modal-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="vfit-history-badge-tag">
                <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
                </svg>
                SO SÁNH KẾT QUẢ AI VÀ ẢNH GỐC
              </span>
              <span className="vfit-badge-fit">
                ✓ {item.fitScore}% Fit
              </span>
            </div>
            <h2 style={{ margin: '0.25rem 0 0 0', fontSize: '1.25rem', fontWeight: 800, color: 'var(--vfit-primary-container)' }}>
              {item.productName}
            </h2>
          </div>
          <button type="button" className="vfit-modal-close" onClick={onClose}>
            ✕
          </button>
        </div>

        {/* Modal Body */}
        <div className="vfit-modal-body">
          {/* Left interactive comparison viewport */}
          <div
            ref={containerRef}
            className="vfit-compare-slider-box"
            onPointerMove={handlePointerMove}
            style={{ cursor: 'ew-resize' }}
          >
            {/* After: AI Result Image (Base) */}
            <img
              src={item.resultPhotoUrl}
              alt="Kết quả AI thử đồ"
              className="vfit-compare-img"
            />

            {/* Before: Original Photo (Clipped) */}
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                bottom: 0,
                width: `${sliderPosition}%`,
                overflow: 'hidden',
                borderRight: '2px solid #fff',
              }}
            >
              <img
                src={item.originalPhotoUrl}
                alt="Ảnh gốc người mẫu"
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: containerRef.current ? `${containerRef.current.clientWidth}px` : '100%',
                  height: '100%',
                  objectFit: 'cover',
                  maxWidth: 'none',
                }}
              />
              <span
                style={{
                  position: 'absolute',
                  top: '1rem',
                  left: '1rem',
                  padding: '0.3rem 0.65rem',
                  borderRadius: '9999px',
                  backgroundColor: 'rgba(0,0,0,0.7)',
                  color: '#fff',
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                }}
              >
                BEFORE • GỐC
              </span>
            </div>

            {/* Label After */}
            <span
              style={{
                position: 'absolute',
                top: '1rem',
                right: '1rem',
                padding: '0.3rem 0.65rem',
                borderRadius: '9999px',
                backgroundColor: 'rgba(8, 10, 97, 0.85)',
                color: '#fff',
                fontSize: '0.7rem',
                fontWeight: 700,
                textTransform: 'uppercase',
              }}
            >
              AFTER • AI 3D
            </span>

            {/* Slider Handle */}
            <div
              className="vfit-compare-handle"
              style={{ left: `${sliderPosition}%` }}
            >
              <div className="vfit-compare-handle-knob">
                ↔
              </div>
            </div>
          </div>

          {/* Right info details */}
          <div className="vfit-compare-side-info">
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--vfit-secondary)' }}>Kích cỡ thử:</span>
                <span style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--vfit-primary-container)' }}>
                  Size {item.size} • {item.colorName}
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--vfit-secondary)' }}>Thời gian thực hiện:</span>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--vfit-on-surface)' }}>
                  {item.date}
                </span>
              </div>

              {/* Fit Zones Breakdown */}
              <div style={{ marginTop: '1.25rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--vfit-secondary)', display: 'block', marginBottom: '0.5rem' }}>
                  Phân tích độ vừa vặn từng vùng:
                </span>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem' }}>
                  {[
                    { key: 'Vai (Shoulder)', data: item.regions.shoulder },
                    { key: 'Ngực (Chest)', data: item.regions.chest },
                    { key: 'Eo (Waist)', data: item.regions.waist },
                    { key: 'Hông (Hip)', data: item.regions.hip },
                  ].map((z) => (
                    <div
                      key={z.key}
                      style={{
                        padding: '0.6rem 0.75rem',
                        borderRadius: 'var(--vfit-radius-md)',
                        backgroundColor: 'var(--vfit-surface-container-low)',
                        border: '1px solid var(--vfit-border-subtle)',
                      }}
                    >
                      <div style={{ fontSize: '0.75rem', color: 'var(--vfit-secondary)' }}>{z.key}</div>
                      <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--vfit-primary-container)', marginTop: '0.1rem' }}>
                        {z.data.text} ({z.data.score}%)
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Notes */}
              {item.notes && (
                <div
                  style={{
                    marginTop: '1rem',
                    padding: '0.75rem',
                    borderRadius: 'var(--vfit-radius-md)',
                    backgroundColor: 'var(--vfit-secondary-container)',
                    color: 'var(--vfit-on-secondary-fixed-variant)',
                    fontSize: '0.8rem',
                    lineHeight: 1.4,
                  }}
                >
                  💡 <strong>Ghi chú AI:</strong> {item.notes}
                </div>
              )}
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', marginTop: '1rem' }}>
              <button
                type="button"
                className="vfit-btn-primary"
                style={{ width: '100%', height: '2.85rem' }}
                onClick={() => {
                  onClose();
                  onReTry(item);
                }}
              >
                THỬ LẠI VỚI SIZE KHÁC
              </button>

              <button
                type="button"
                className="vfit-btn-secondary"
                style={{ width: '100%', height: '2.85rem' }}
                onClick={handleDownload}
              >
                <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" />
                </svg>
                Tải ảnh HD kết quả
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
