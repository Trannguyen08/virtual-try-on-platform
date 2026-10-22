import React, { useState, useMemo, useEffect } from 'react';
import { TryOnHistoryItem } from '../../data/mockHistory';
import { historyStorage } from '../../services/historyStorage';
import { HistoryStatsBar } from '../../components/history/HistoryStatsBar';
import { HistoryToolbar, HistoryFilterState } from '../../components/history/HistoryToolbar';
import { HistoryCard } from '../../components/history/HistoryCard';
import { Garment360Viewer } from '../../viewer/Garment360Viewer';

interface HistoryPageProps {
  onStartTryOn: () => void;
  onView3DItem: (item: TryOnHistoryItem) => void;
  onReTryItem: (item: TryOnHistoryItem) => void;
}

export const HistoryPage: React.FC<HistoryPageProps> = ({
  onStartTryOn,
  onView3DItem,
  onReTryItem,
}) => {
  const [historyItems, setHistoryItems] = useState<TryOnHistoryItem[]>([]);
  const [activeViewerItem, setActiveViewerItem] = useState<TryOnHistoryItem | null>(null);

  const [filters, setFilters] = useState<HistoryFilterState>({
    searchQuery: '',
    timeRange: 'all',
    category: 'all',
    resultType: 'all',
  });

  // Refresh while the page is open so entries disappear when their short retention expires.
  useEffect(() => {
    const refresh = () => setHistoryItems(historyStorage.getHistory());
    refresh();
    const timer = window.setInterval(refresh, 5_000);
    return () => window.clearInterval(timer);
  }, []);

  const handleDelete = (id: string) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa lượt thử đồ này khỏi lịch sử không?')) {
      const updated = historyStorage.deleteItem(id);
      setHistoryItems(updated);
    }
  };

  const handleClearHistory = () => {
    if (!window.confirm('Xóa toàn bộ lượt thử đồ đang lưu trong 5 phút gần đây?')) return;
    historyStorage.clearAll();
    setHistoryItems([]);
  };

  const handleViewHistoryItem = (item: TryOnHistoryItem) => {
    if (item.resultAssetUrl) setActiveViewerItem(item);
    else onView3DItem(item);
  };

  const handleResetFilters = () => {
    setFilters({
      searchQuery: '',
      timeRange: 'all',
      category: 'all',
      resultType: 'all',
    });
  };

  // Filtered Items logic
  const filteredItems = useMemo(() => {
    return historyItems.filter((item) => {
      // 1. Search query
      if (filters.searchQuery.trim()) {
        const q = filters.searchQuery.toLocaleLowerCase('vi');
        const matchesName = item.productName.toLocaleLowerCase('vi').includes(q);
        const matchesCategory = item.categoryLabel.toLocaleLowerCase('vi').includes(q);
        const matchesNotes = item.notes?.toLocaleLowerCase('vi').includes(q) || false;
        if (!matchesName && !matchesCategory && !matchesNotes) return false;
      }

      // 2. Category
      if (filters.category !== 'all' && item.category !== filters.category) {
        return false;
      }

      // Time ranges use the record timestamp, not a hard-coded month label.
      const itemDate = new Date(item.timestamp);
      const now = new Date();
      if (filters.timeRange === 'today'
          && (itemDate.getFullYear() !== now.getFullYear()
            || itemDate.getMonth() !== now.getMonth()
            || itemDate.getDate() !== now.getDate())) return false;
      if (filters.timeRange === '7days' && Date.now() - item.timestamp > 7 * 24 * 60 * 60 * 1000) return false;
      if (filters.timeRange === 'this-month'
          && (itemDate.getFullYear() !== now.getFullYear() || itemDate.getMonth() !== now.getMonth())) return false;

      if (filters.resultType === 'simulated' && !item.simulationRan) return false;
      if (filters.resultType === 'preview' && item.simulationRan) return false;

      return true;
    });
  }, [historyItems, filters]);

  return (
    <div className="vfit-history-page">
      {/* 1. Header & Quick Stat Metric Strip */}
      <HistoryStatsBar items={historyItems} onClear={handleClearHistory} />

      {/* 2. Search & Multi-criteria Filtering Toolbar */}
      <HistoryToolbar
        filters={filters}
        onFilterChange={setFilters}
        onReset={handleResetFilters}
      />

      {/* 3. Grid of History Results or Empty State */}
      {filteredItems.length > 0 ? (
        <div className="vfit-history-grid">
          {filteredItems.map((item) => (
            <HistoryCard
              key={item.id}
              item={item}
              onView3D={handleViewHistoryItem}
              onDelete={handleDelete}
              onReTry={(selected) => onReTryItem(selected)}
            />
          ))}
        </div>
      ) : (
        <div
          style={{
            textAlign: 'center',
            padding: '4rem 1.5rem',
            backgroundColor: 'var(--vfit-surface-card)',
            borderRadius: 'var(--vfit-radius-xl)',
            border: '1px dashed var(--vfit-border-subtle)',
          }}
        >
          <div style={{ fontSize: '1rem', marginBottom: '1rem', fontWeight: 700 }}>Lịch sử thử đồ</div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--vfit-on-surface)' }}>
            {historyItems.length === 0 ? 'Chưa có lượt thử đồ gần đây' : 'Không tìm thấy lượt thử đồ phù hợp'}
          </h3>
          <p style={{ color: 'var(--vfit-secondary)', maxWidth: '420px', margin: '0.5rem auto 1.5rem auto', fontSize: '0.9rem' }}>
            {historyItems.length === 0
              ? 'Kết quả thử đồ hoàn tất sẽ xuất hiện tại đây và tự xóa sau 5 phút.'
              : 'Thử đổi từ khóa hoặc bộ lọc để xem các lượt thử gần đây.'}
          </p>
          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
            <button
              type="button"
              className="vfit-btn-secondary"
              onClick={handleResetFilters}
              style={{ width: 'auto' }}
            >
              Đặt lại bộ lọc
            </button>
            <button
              type="button"
              className="vfit-btn-primary"
              onClick={onStartTryOn}
              style={{ width: 'auto', padding: '0 1.5rem' }}
            >
              Thử đồ trang phục mới
            </button>
          </div>
        </div>
      )}

      {activeViewerItem?.resultAssetUrl && (
        <div className="vfit-history-viewer-backdrop" role="presentation" onClick={() => setActiveViewerItem(null)}>
          <section
            className="vfit-history-viewer-dialog"
            role="dialog"
            aria-modal="true"
            aria-label={`Kết quả 3D: ${activeViewerItem.productName}`}
            onClick={(event) => event.stopPropagation()}
          >
            <header>
              <div><span>KẾT QUẢ THỬ ĐỒ</span><h2>{activeViewerItem.productName}</h2></div>
              <button type="button" onClick={() => setActiveViewerItem(null)} aria-label="Đóng">Đóng</button>
            </header>
            <Garment360Viewer modelUrl={activeViewerItem.resultAssetUrl} subject="garment" />
            <p>{activeViewerItem.simulationRan ? 'Mô phỏng đã hoàn tất.' : 'Bản xem trước; chưa mô phỏng vải.'} Chưa có đánh giá độ vừa vặn cho kết quả này.</p>
          </section>
        </div>
      )}

    </div>
  );
};
