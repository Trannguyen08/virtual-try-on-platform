import React from 'react';

export interface HistoryFilterState {
  searchQuery: string;
  timeRange: string;
  category: string;
  fitLevel: string;
}

interface HistoryToolbarProps {
  filters: HistoryFilterState;
  onFilterChange: (filters: HistoryFilterState) => void;
  onReset: () => void;
}

export const HistoryToolbar: React.FC<HistoryToolbarProps> = ({
  filters,
  onFilterChange,
  onReset,
}) => {
  return (
    <div className="vfit-history-toolbar">
      {/* Search Input */}
      <div className="vfit-search-box">
        <svg
          className="vfit-search-icon"
          width="18"
          height="18"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          viewBox="0 0 24 24"
        >
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          type="text"
          placeholder="Tìm kiếm theo tên sản phẩm, bộ sưu tập..."
          value={filters.searchQuery}
          onChange={(e) =>
            onFilterChange({ ...filters, searchQuery: e.target.value })
          }
        />
      </div>

      {/* Dropdown Filters */}
      <div className="vfit-filter-group">
        {/* Time Filter */}
        <div className="vfit-select-wrap">
          <select
            value={filters.timeRange}
            onChange={(e) =>
              onFilterChange({ ...filters, timeRange: e.target.value })
            }
          >
            <option value="all">Thời gian: Tất cả</option>
            <option value="today">Hôm nay</option>
            <option value="7days">7 ngày qua</option>
            <option value="this-month">Tháng 9/2026</option>
          </select>
          <svg
            className="vfit-select-arrow"
            width="16"
            height="16"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            viewBox="0 0 24 24"
          >
            <path d="M6 9l6 6 6-6" />
          </svg>
        </div>

        {/* Category Filter */}
        <div className="vfit-select-wrap">
          <select
            value={filters.category}
            onChange={(e) =>
              onFilterChange({ ...filters, category: e.target.value })
            }
          >
            <option value="all">Danh mục: Tất cả</option>
            <option value="t_shirt">Áo thun</option>
            <option value="shirt">Áo sơ mi</option>
            <option value="dress">Váy đầm</option>
            <option value="jacket">Áo khoác</option>
            <option value="pants">Quần & Chân váy</option>
          </select>
          <svg
            className="vfit-select-arrow"
            width="16"
            height="16"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            viewBox="0 0 24 24"
          >
            <path d="M6 9l6 6 6-6" />
          </svg>
        </div>

        {/* Fit Score Filter */}
        <div className="vfit-select-wrap">
          <select
            value={filters.fitLevel}
            onChange={(e) =>
              onFilterChange({ ...filters, fitLevel: e.target.value })
            }
          >
            <option value="all">Độ khớp: Tất cả</option>
            <option value="98">&gt;98% Chuẩn dáng cao</option>
            <option value="95-98">95% - 98% Tiêu chuẩn</option>
            <option value="under95">&lt;95% Khuyên thử lại</option>
          </select>
          <svg
            className="vfit-select-arrow"
            width="16"
            height="16"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            viewBox="0 0 24 24"
          >
            <path d="M6 9l6 6 6-6" />
          </svg>
        </div>

        {/* Reset button */}
        {(filters.searchQuery ||
          filters.timeRange !== 'all' ||
          filters.category !== 'all' ||
          filters.fitLevel !== 'all') && (
          <button
            type="button"
            onClick={onReset}
            style={{
              height: '2.75rem',
              padding: '0 1rem',
              borderRadius: 'var(--vfit-radius-lg)',
              backgroundColor: 'var(--vfit-surface-container)',
              border: '1px solid var(--vfit-border-subtle)',
              color: 'var(--vfit-primary-container)',
              fontSize: '0.8rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
            }}
          >
            ✕ Xóa lọc
          </button>
        )}
      </div>
    </div>
  );
};
