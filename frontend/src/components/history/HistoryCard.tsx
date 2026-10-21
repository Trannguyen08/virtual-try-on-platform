import React from 'react';
import { TryOnHistoryItem } from '../../data/mockHistory';

interface HistoryCardProps {
  item: TryOnHistoryItem;
  onCompare: (item: TryOnHistoryItem) => void;
  onView3D: (item: TryOnHistoryItem) => void;
  onDelete: (id: string) => void;
  onToggleCart: (id: string) => void;
  onReTry: (item: TryOnHistoryItem) => void;
}

export const HistoryCard: React.FC<HistoryCardProps> = ({
  item,
  onCompare,
  onView3D,
  onDelete,
  onToggleCart,
}) => {
  const handleDownload = (e: React.MouseEvent) => {
    e.stopPropagation();
    const link = document.createElement('a');
    link.href = item.resultPhotoUrl;
    link.download = `VFit-AI-${item.productName.replace(/\s+/g, '-')}.jpg`;
    link.target = '_blank';
    link.click();
  };

  return (
    <div className="vfit-history-card">
      {/* Media container */}
      <div className="vfit-history-card-media">
        <img
          src={item.resultPhotoUrl}
          alt={item.productName}
          loading="lazy"
        />

        {/* Top-left Badges */}
        <div className="vfit-card-badge-left">
          <span className="vfit-badge-after">AFTER • AI SIM</span>
          <span className="vfit-badge-fit">
            <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
              <path d="M20 6L9 17l-5-5" />
            </svg>
            {item.fitScore}% Fit
          </span>
        </div>

        {/* Top-right Cart / Bookmark badge */}
        <div className="vfit-card-badge-right">
          <button
            type="button"
            className="vfit-cart-indicator"
            onClick={(e) => {
              e.stopPropagation();
              onToggleCart(item.id);
            }}
            title={item.inCart ? 'Đã thêm vào giỏ hàng' : 'Thêm vào giỏ hàng'}
            aria-label="Toggle cart"
          >
            <svg width="16" height="16" fill={item.inCart ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4zM3 6h18M16 10a4 4 0 0 1-8 0" />
            </svg>
          </button>
        </div>

        {/* Bottom hover action: Compare Before/After */}
        <div
          className="vfit-compare-hover-trigger"
          onClick={() => onCompare(item)}
          title="Nhấn để xem so sánh Before/After"
        >
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--vfit-on-surface)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
            So sánh ảnh gốc
          </span>
          <span style={{ fontSize: '0.7rem', fontWeight: 700, padding: '0.2rem 0.5rem', borderRadius: '9999px', backgroundColor: 'var(--vfit-tertiary-fixed)', color: 'var(--vfit-on-tertiary-fixed-variant)' }}>
            3D Mode
          </span>
        </div>
      </div>

      {/* Card Info Body */}
      <div className="vfit-history-card-body">
        <div>
          <div className="vfit-card-title-price">
            <h3 title={item.productName}>{item.productName}</h3>
            <span className="vfit-card-price">{item.formattedPrice}</span>
          </div>

          <div className="vfit-card-meta">
            Ngày thử: {item.date} <br />
            Size: <strong style={{ color: 'var(--vfit-on-surface)' }}>{item.size}</strong> • Màu: {item.colorName}
          </div>

          <div>
            {item.inCart ? (
              <span className="vfit-card-status-pill vfit-status-in-cart">
                <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                  <path d="M20 6L9 17l-5-5" />
                </svg>
                Đã thêm vào giỏ hàng
              </span>
            ) : (
              <span className="vfit-card-status-pill vfit-status-not-in-cart">
                <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 6v6l4 2" />
                </svg>
                Chưa thêm vào giỏ
              </span>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="vfit-card-actions">
          <button
            type="button"
            className="vfit-btn-view-3d"
            onClick={() => onView3D(item)}
            title="Xem lại và xoay 360 độ"
          >
            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
              <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
              <line x1="12" y1="22.08" x2="12" y2="12" />
            </svg>
            <span>Xem lại 3D</span>
          </button>

          <button
            type="button"
            className="vfit-btn-icon-action"
            onClick={handleDownload}
            title="Tải ảnh HD về máy"
            aria-label="Download HD image"
          >
            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" />
            </svg>
          </button>

          <button
            type="button"
            className="vfit-btn-icon-action delete"
            onClick={() => onDelete(item.id)}
            title="Xóa khỏi lịch sử"
            aria-label="Delete history item"
          >
            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};
