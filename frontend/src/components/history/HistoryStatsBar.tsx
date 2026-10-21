import React from 'react';
import { TryOnHistoryItem } from '../../data/mockHistory';

interface HistoryStatsBarProps {
  items: TryOnHistoryItem[];
}

export const HistoryStatsBar: React.FC<HistoryStatsBarProps> = ({ items }) => {
  const totalCount = items.length;
  const avgFit =
    totalCount > 0
      ? (items.reduce((acc, curr) => acc + curr.fitScore, 0) / totalCount).toFixed(1)
      : '0.0';
  const cartCount = items.filter((i) => i.inCart).length;

  return (
    <div className="vfit-history-top">
      <div className="vfit-history-title-group">
        <div className="vfit-history-badge-tag">
          <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
          </svg>
          BỘ SƯU TẬP CÁ NHÂN & LOOKBOOK ẢO
        </div>
        <h1>LỊCH SỬ THỬ ĐỒ ẢO</h1>
        <p>
          Xem lại tất cả kết quả mô phỏng trang phục 3D trên vóc dáng của bạn, so sánh trước sau hoặc thử lại kích cỡ mới.
        </p>
      </div>

      <div className="vfit-stats-strip">
        {/* Total tries */}
        <div className="vfit-stat-chip">
          <div className="vfit-stat-dot" style={{ backgroundColor: 'var(--vfit-focus-ring)' }} />
          <div>
            <div className="vfit-stat-label">Tổng lượt thử</div>
            <div className="vfit-stat-val">{totalCount} Lần thử đồ</div>
          </div>
        </div>

        {/* Avg fit rate */}
        <div className="vfit-stat-chip">
          <div className="vfit-stat-dot" style={{ backgroundColor: 'var(--vfit-surface-tint)' }} />
          <div>
            <div className="vfit-stat-label">Độ khớp trung bình</div>
            <div className="vfit-stat-val" style={{ color: 'var(--vfit-primary-container)' }}>
              {avgFit}% Chuẩn dáng
            </div>
          </div>
        </div>

        {/* Cart items */}
        <div className="vfit-stat-chip">
          <div className="vfit-stat-dot" style={{ backgroundColor: 'var(--vfit-destructive-crimson)' }} />
          <div>
            <div className="vfit-stat-label">Giỏ mua sắm</div>
            <div className="vfit-stat-val">{cartCount} Đã thêm giỏ</div>
          </div>
        </div>
      </div>
    </div>
  );
};
