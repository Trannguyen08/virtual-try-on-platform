import React, { useRef, useState } from 'react';

interface UploadStepProps {
  onNext: (photoFile: File | null, photoPreviewUrl: string, heightCm: number) => void;
}

export const UploadStep: React.FC<UploadStepProps> = ({ onNext }) => {
  const [photoPreview, setPhotoPreview] = useState<string>('https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&auto=format&fit=crop&q=80');
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [heightCm, setHeightCm] = useState<number>(170);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Model Presets
  const presets = [
    {
      name: 'Linh Đan (Nữ)',
      stats: '1m68 • 50kg',
      height: 168,
      img: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500&auto=format&fit=crop&q=80',
    },
    {
      name: 'Minh Quân (Nam)',
      stats: '1m80 • 74kg',
      height: 180,
      img: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500&auto=format&fit=crop&q=80',
    },
    {
      name: 'Mai Anh (Nữ)',
      stats: '1m72 • 52kg',
      height: 172,
      img: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=500&auto=format&fit=crop&q=80',
    },
    {
      name: 'Thanh Trúc (Curvy)',
      stats: '1m65 • 68kg',
      height: 165,
      img: 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=500&auto=format&fit=crop&q=80',
    },
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setPhotoFile(file);
      setPhotoPreview(URL.createObjectURL(file));
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setPhotoFile(file);
      setPhotoPreview(URL.createObjectURL(file));
    }
  };

  const handleSelectPreset = (preset: typeof presets[0]) => {
    setPhotoPreview(preset.img);
    setPhotoFile(null);
    setHeightCm(preset.height);
  };

  const handleContinue = () => {
    onNext(photoFile, photoPreview, heightCm);
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem', alignItems: 'start' }}>
      {/* Left Column: Dropzone & Height Control */}
      <div>
        <div style={{ backgroundColor: 'var(--vfit-surface-card)', borderRadius: 'var(--vfit-radius-xl)', padding: '2rem', boxShadow: '0 2px 10px rgba(8,10,97,0.03)' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', padding: '0.25rem 0.75rem', borderRadius: '9999px', backgroundColor: 'var(--vfit-secondary-container)', color: 'var(--vfit-primary-container)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.5rem' }}>
            <span>📸 Bước 1 • Tải ảnh & Số đo</span>
          </div>

          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--vfit-on-surface)', margin: '0 0 0.5rem 0', letterSpacing: '-0.02em' }}>
            ẢNH CHÂN DUNG CỦA BẠN
          </h2>
          <p style={{ color: 'var(--vfit-secondary)', fontSize: '0.9rem', lineHeight: '1.5', margin: '0 0 1.5rem 0' }}>
            Tải ảnh toàn thân rõ nét để AI lập bản đồ 3D vóc dáng và ướm đồ chuẩn xác từng nếp vải.
          </p>

          {/* Interactive Dropzone */}
          <div
            className={`vfit-dropzone ${isDragOver ? 'drag-active' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              accept="image/png, image/jpeg, image/jpg"
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />

            {photoPreview ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
                <img
                  src={photoPreview}
                  alt="Ảnh đã chọn"
                  style={{ width: '130px', height: '175px', objectFit: 'cover', borderRadius: '0.75rem', boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}
                />
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--vfit-on-surface)' }}>
                    {photoFile ? photoFile.name : 'Ảnh người mẫu mẫu'}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--vfit-focus-ring)', fontWeight: 600, marginTop: '0.2rem' }}>
                    ✓ Sẵn sàng quét phân tích 3D
                  </div>
                  <button
                    type="button"
                    style={{ marginTop: '0.65rem', background: 'none', border: 'none', color: 'var(--vfit-secondary)', textDecoration: 'underline', fontSize: '0.8rem', cursor: 'pointer' }}
                  >
                    Bấm để đổi ảnh khác
                  </button>
                </div>
              </div>
            ) : (
              <div>
                <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>☁️</div>
                <div style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--vfit-on-surface)' }}>
                  Kéo thả ảnh toàn thân vào đây
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--vfit-secondary)', margin: '0.35rem 0 1rem 0' }}>
                  hoặc chọn tệp từ máy tính / điện thoại
                </div>
                <button type="button" className="vfit-btn-primary" style={{ display: 'inline-flex', width: 'auto', padding: '0 1.5rem', height: '2.75rem' }}>
                  CHỌN ẢNH TỪ THIẾT BỊ
                </button>
              </div>
            )}
          </div>

          {/* Height input slider (140 - 210 cm) */}
          <div className="vfit-height-control">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--vfit-on-surface)' }}>
                Chiều cao cơ thể (cm)
              </span>
              <div className="vfit-height-val-display">{heightCm} cm</div>
            </div>
            <input
              type="range"
              min="140"
              max="210"
              value={heightCm}
              onChange={(e) => setHeightCm(Number(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--vfit-primary-container)', cursor: 'pointer' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--vfit-outline)' }}>
              <span>140 cm</span>
              <span>175 cm (chuẩn)</span>
              <span>210 cm</span>
            </div>
          </div>

          {/* Quick Select Presets */}
          <div style={{ marginTop: '1.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--vfit-on-surface)', textTransform: 'uppercase' }}>
              Hoặc thử nhanh với người mẫu chuẩn AI:
            </span>
            <div className="vfit-preset-grid">
              {presets.map((preset, idx) => (
                <button
                  key={idx}
                  type="button"
                  className={`vfit-preset-card ${photoPreview === preset.img ? 'selected' : ''}`}
                  onClick={() => handleSelectPreset(preset)}
                >
                  <img src={preset.img} alt={preset.name} />
                  <div className="vfit-preset-overlay">
                    <span style={{ fontSize: '0.75rem', fontWeight: 700 }}>{preset.name}</span>
                    <span style={{ fontSize: '0.65rem', color: '#cbd5e1' }}>{preset.stats}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Right Column: Best Photo Guidelines & Action */}
      <div>
        <div style={{ backgroundColor: 'var(--vfit-surface-card)', borderRadius: 'var(--vfit-radius-xl)', padding: '2rem', boxShadow: '0 2px 10px rgba(8,10,97,0.03)' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--vfit-on-surface)', margin: '0 0 0.5rem 0' }}>
            TIÊU CHUẨN ĐỂ ĐẠT KẾT QUẢ ĐẸP NHẤT
          </h3>
          <p style={{ color: 'var(--vfit-secondary)', fontSize: '0.875rem', margin: '0 0 1.25rem 0' }}>
            Độ tương thích trang phục 3D phụ thuộc trực tiếp vào tư thế và ánh sáng trong ảnh gốc.
          </p>

          {/* DOs */}
          <div className="vfit-guide-card vfit-guide-dos">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, color: 'var(--vfit-primary-container)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
              <span>✓</span>
              <span>NÊN LỰA CHỌN</span>
            </div>
            <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.85rem', color: 'var(--vfit-on-surface)', lineHeight: '1.6' }}>
              <li><strong>Toàn thân:</strong> Thấy rõ từ đầu đến chân trong khung hình.</li>
              <li><strong>Tư thế:</strong> Đứng thẳng tự nhiên, hai tay thả lỏng nhẹ hai bên.</li>
              <li><strong>Ánh sáng:</strong> Đủ sáng, không bị bóng đổ sẫm màu.</li>
              <li><strong>Hậu cảnh:</strong> Phông nền đơn giản, ít đồ đạc xung quanh.</li>
            </ul>
          </div>

          {/* DONTs */}
          <div className="vfit-guide-card vfit-guide-donts">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, color: 'var(--vfit-destructive-crimson)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
              <span>✕</span>
              <span>CẦN TRÁNH</span>
            </div>
            <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.85rem', color: 'var(--vfit-on-surface)', lineHeight: '1.6' }}>
              <li>Ảnh bị mất phần chân hoặc chụp góc nghiêng quá lệch.</li>
              <li>Tư thế ngồi hoặc khoanh tay che khuất vùng ngực và eo.</li>
              <li>Chụp nhóm nhiều người cùng xuất hiện trong ảnh.</li>
            </ul>
          </div>

          {/* Continue CTA */}
          <div style={{ marginTop: '1.75rem' }}>
            <button
              type="button"
              className="vfit-btn-primary"
              style={{ width: '100%', height: '3.25rem', fontSize: '1rem' }}
              onClick={handleContinue}
            >
              <span>TIẾP TỤC CHỌN ĐỒ</span>
              <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
