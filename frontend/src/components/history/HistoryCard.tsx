import React from 'react';
import { TryOnHistoryItem } from '../../data/mockHistory';

interface HistoryCardProps {
  item: TryOnHistoryItem;
  onView3D: (item: TryOnHistoryItem) => void;
  onDelete: (id: string) => void;
  onReTry: (item: TryOnHistoryItem) => void;
}

export const HistoryCard: React.FC<HistoryCardProps> = ({ item, onView3D, onDelete, onReTry }) => {
  const resultLabel = item.simulationRan ? 'Đã mô phỏng' : 'Bản xem trước';
  const dateLabel = new Date(item.timestamp).toLocaleString('vi-VN', {
    day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit',
  });

  return (
    <article className="vfit-history-card">
      <div className="vfit-history-card-media">
        {item.resultPhotoUrl ? (
          <>
            <img src={item.resultPhotoUrl} alt={`Ảnh tham chiếu: ${item.productName}`} loading="lazy" />
            <small className="vfit-history-media-caption">Ảnh sản phẩm tham chiếu</small>
          </>
        ) : (
          <div className="vfit-history-placeholder" aria-label="Không lưu ảnh cá nhân">
            <span aria-hidden="true">3D</span>
            <small>Ảnh riêng không được lưu</small>
          </div>
        )}
        <div className="vfit-card-badge-left">
          <span className="vfit-badge-after">{item.resultAssetUrl ? 'KẾT QUẢ 3D' : 'LỊCH SỬ'}</span>
          <span className={`vfit-badge-result${item.simulationRan ? ' is-simulated' : ''}`}>{resultLabel}</span>
        </div>
      </div>

      <div className="vfit-history-card-body">
        <div className="vfit-history-card-heading">
          <div className="vfit-card-title-price">
            <h3 title={item.productName}>{item.productName}</h3>
            {item.formattedPrice && <span className="vfit-card-price">{item.formattedPrice}</span>}
          </div>
          <p className="vfit-card-meta">
            {item.categoryLabel} · {dateLabel}
            {item.size && item.size !== '—' ? <> · Nhãn size {item.size}</> : null}
          </p>
          {item.notes && <p className="vfit-history-note">{item.notes}</p>}
          {item.fitScore == null && <p className="vfit-history-honesty">Chưa có đánh giá độ vừa vặn cho lượt thử này.</p>}
        </div>

        <div className="vfit-card-actions">
          <button type="button" className="vfit-btn-view-3d" onClick={() => onView3D(item)}>
            {item.resultAssetUrl ? 'Xem lại 3D' : 'Mở lại sản phẩm'}
          </button>
          {item.resultAssetUrl && <a className="vfit-btn-action" href={item.resultAssetUrl} download title="Tải kết quả 3D" aria-label="Tải kết quả 3D">Tải</a>}
          {item.source !== 'upload' && (
            <button type="button" className="vfit-btn-action" onClick={() => onReTry(item)} title="Thử lại sản phẩm" aria-label="Thử lại sản phẩm">
              Thử lại
            </button>
          )}
          <button type="button" className="vfit-btn-action delete" onClick={() => onDelete(item.id)} title="Xóa lượt thử" aria-label="Xóa lượt thử">
            Xóa
          </button>
        </div>
      </div>
    </article>
  );
};
