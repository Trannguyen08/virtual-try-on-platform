import React from 'react';
import { TryOnHistoryItem } from '../../data/mockHistory';

interface HistoryStatsBarProps {
  items: TryOnHistoryItem[];
  onClear: () => void;
}

export const HistoryStatsBar: React.FC<HistoryStatsBarProps> = ({ items, onClear }) => {
  const totalCount = items.length;
  const simulatedCount = items.filter((item) => item.simulationRan).length;
  const previewCount = totalCount - simulatedCount;

  return (
    <div className="vfit-history-top">
      <div className="vfit-history-title-group">
        <div className="vfit-history-badge-tag">
          <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
          </svg>
          LỊCH SỬ THỬ ĐỒ GẦN ĐÂY · TỰ XÓA SAU 5 PHÚT
        </div>
        <h1>LỊCH SỬ THỬ ĐỒ ẢO</h1>
        <p>
          Các lượt thử đồ đã hoàn tất trên thiết bị này. Ảnh cá nhân không được lưu vào lịch sử.
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

        {/* Completed simulations */}
        <div className="vfit-stat-chip">
          <div className="vfit-stat-dot" style={{ backgroundColor: '#26a269' }} />
          <div>
            <div className="vfit-stat-label">Đã mô phỏng</div>
            <div className="vfit-stat-val" style={{ color: 'var(--vfit-primary-container)' }}>
              {simulatedCount} lượt
            </div>
          </div>
        </div>

        {/* Preview results */}
        <div className="vfit-stat-chip">
          <div className="vfit-stat-dot" style={{ backgroundColor: '#8b5cf6' }} />
          <div>
            <div className="vfit-stat-label">Bản xem trước</div>
            <div className="vfit-stat-val">{previewCount} lượt</div>
          </div>
        </div>
      </div>
      {totalCount > 0 && <button type="button" className="vfit-history-clear" onClick={onClear}>Xóa lịch sử</button>}
    </div>
  );
};
