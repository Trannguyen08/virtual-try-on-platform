import React, { useRef, useState } from 'react';
import { BodyCustomParams, BodyPreset, BODY_PRESETS } from '../../data/bodyPresets';
import { BodyMorphingPanel } from './BodyMorphingPanel';

interface UploadStepProps {
  initialCustomParams?: BodyCustomParams;
  onNext: (
    photoFile: File | null,
    photoPreviewUrl: string,
    heightCm: number,
    customParams: BodyCustomParams
  ) => void;
}

const defaultInitialParams: BodyCustomParams = {
  height: 170,
  weight: 50,
  gender: 'female',
  age: 24,
  skinTone: 'light',
  skinColorHex: '#f5d0b5',
  selectedPresetId: 'slim',
  glbModelUrl: '/models/body_default.glb',
  proportions: {
    shoulder_width: 0.35,
    waist: 0.28,
    hips: 0.35,
    chest: 0.35,
    belly: 0.05,
    muscle_tone: 0.2,
    leg_length: 0.6,
    arm_length: 0.5,
    buttocks: 0.4,
  },
};

export const UploadStep: React.FC<UploadStepProps> = ({ initialCustomParams, onNext }) => {
  const [customParams, setCustomParams] = useState<BodyCustomParams>(
    initialCustomParams || defaultInitialParams
  );
  const [photoPreview, setPhotoPreview] = useState<string>(
    BODY_PRESETS[0].img
  );
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [heightCm, setHeightCm] = useState<number>(customParams.height || 170);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  const handleSelectPreset = (preset: BodyPreset) => {
    setPhotoPreview(preset.img);
    setPhotoFile(null);
    setHeightCm(preset.height);
    setCustomParams({
      ...customParams,
      height: preset.height,
      weight: preset.weight,
      gender: preset.gender,
      selectedPresetId: preset.id,
      glbModelUrl: preset.glbModelUrl,
      proportions: { ...preset.proportions },
    });
  };

  const handleCustomParamsChange = (newParams: BodyCustomParams) => {
    setCustomParams(newParams);
    if (newParams.height !== heightCm) {
      setHeightCm(newParams.height);
    }
  };

  const handleHeightSliderChange = (newHeight: number) => {
    setHeightCm(newHeight);
    setCustomParams((prev) => ({
      ...prev,
      height: newHeight,
    }));
  };

  const handleContinue = () => {
    onNext(photoFile, photoPreview, heightCm, customParams);
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
              onChange={(e) => handleHeightSliderChange(Number(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--vfit-primary-container)', cursor: 'pointer' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--vfit-outline)' }}>
              <span>140 cm</span>
              <span>175 cm (chuẩn)</span>
              <span>210 cm</span>
            </div>
          </div>

          {/* Biometric Morphing & Preset Panel */}
          <BodyMorphingPanel
            customParams={customParams}
            onChange={handleCustomParamsChange}
            onSelectPreset={handleSelectPreset}
          />
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

          {/* AI Photo Validation Inspection Check */}
          <div
            style={{
              marginTop: '1.25rem',
              padding: '1rem',
              borderRadius: 'var(--vfit-radius-lg)',
              backgroundColor: 'var(--vfit-surface-container-low)',
              border: '1px solid rgba(61, 126, 255, 0.2)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--vfit-focus-ring)', letterSpacing: '0.05em', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <span className="vfit-pulse-dot" />
                KIỂM TRA ẢNH AI ĐẠT CHUẨN
              </span>
              <span style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--vfit-primary-container)' }}>
                99.2 / 100 Điểm
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.4rem', fontSize: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: 'var(--vfit-on-surface)' }}>
                <span style={{ color: '#16a34a', fontWeight: 800 }}>✓</span> Tư thế đứng thẳng (100%)
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: 'var(--vfit-on-surface)' }}>
                <span style={{ color: '#16a34a', fontWeight: 800 }}>✓</span> Ánh sáng rõ nét (98%)
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: 'var(--vfit-on-surface)' }}>
                <span style={{ color: '#16a34a', fontWeight: 800 }}>✓</span> Toàn thân cân đối (99%)
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: 'var(--vfit-on-surface)' }}>
                <span style={{ color: '#16a34a', fontWeight: 800 }}>✓</span> Tách phông nền sẵn sàng
              </div>
            </div>
          </div>

          {/* Continue CTA */}
          <div style={{ marginTop: '1.25rem' }}>
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
