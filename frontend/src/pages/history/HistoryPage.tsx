import React, { useState, useMemo, useEffect } from 'react';
import { TryOnHistoryItem } from '../../data/mockHistory';
import { historyStorage } from '../../services/historyStorage';
import { HistoryStatsBar } from '../../components/history/HistoryStatsBar';
import { HistoryToolbar, HistoryFilterState } from '../../components/history/HistoryToolbar';
import { HistoryCard } from '../../components/history/HistoryCard';
import { CompareModal } from '../../components/history/CompareModal';

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
  const [activeCompareItem, setActiveCompareItem] = useState<TryOnHistoryItem | null>(null);

  const [filters, setFilters] = useState<HistoryFilterState>({
    searchQuery: '',
    timeRange: 'all',
    category: 'all',
    fitLevel: 'all',
  });

  // Load from local storage
  useEffect(() => {
    const loaded = historyStorage.getHistory();
    setHistoryItems(loaded);
  }, []);

  const handleDelete = (id: string) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa lượt thử đồ này khỏi lịch sử không?')) {
      const updated = historyStorage.deleteItem(id);
      setHistoryItems(updated);
    }
  };

  const handleToggleCart = (id: string) => {
    const updated = historyStorage.toggleCart(id);
    setHistoryItems(updated);
  };

  const handleResetFilters = () => {
    setFilters({
      searchQuery: '',
      timeRange: 'all',
      category: 'all',
      fitLevel: 'all',
    });
  };

  // Filtered Items logic
  const filteredItems = useMemo(() => {
    return historyItems.filter((item) => {
      // 1. Search query
      if (filters.searchQuery.trim()) {
        const q = filters.searchQuery.toLowerCase();
        const matchesName = item.productName.toLowerCase().includes(q);
        const matchesCategory = item.categoryLabel.toLowerCase().includes(q);
        const matchesColor = item.colorName.toLowerCase().includes(q);
        if (!matchesName && !matchesCategory && !matchesColor) return false;
      }

      // 2. Category
      if (filters.category !== 'all' && item.category !== filters.category) {
        return false;
      }

      // 3. Fit Level
      if (filters.fitLevel === '98' && item.fitScore < 98) {
        return false;
      }
      if (filters.fitLevel === '95-98' && (item.fitScore < 95 || item.fitScore >= 98)) {
        return false;
      }
      if (filters.fitLevel === 'under95' && item.fitScore >= 95) {
        return false;
      }

      return true;
    });
  }, [historyItems, filters]);

  return (
    <div className="vfit-history-page">
      {/* 1. Header & Quick Stat Metric Strip */}
      <HistoryStatsBar items={historyItems} />

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
              onCompare={(selected) => setActiveCompareItem(selected)}
              onView3D={(selected) => onView3DItem(selected)}
              onDelete={handleDelete}
              onToggleCart={handleToggleCart}
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
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--vfit-on-surface)' }}>
            Không tìm thấy kết quả thử đồ phù hợp
          </h3>
          <p style={{ color: 'var(--vfit-secondary)', maxWidth: '420px', margin: '0.5rem auto 1.5rem auto', fontSize: '0.9rem' }}>
            Không có lần thử nào khớp với bộ lọc hiện tại của bạn. Hãy thử thay đổi từ khóa hoặc đặt lại bộ lọc.
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

      {/* 4. Compare Modal Popup (Before / After interactive slider) */}
      {activeCompareItem && (
        <CompareModal
          item={activeCompareItem}
          onClose={() => setActiveCompareItem(null)}
          onReTry={(selected) => {
            setActiveCompareItem(null);
            onReTryItem(selected);
          }}
        />
      )}
    </div>
  );
};
