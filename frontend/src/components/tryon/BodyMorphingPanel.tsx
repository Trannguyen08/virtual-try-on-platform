import React, { useState } from 'react';
import { BODY_PRESETS, BodyCustomParams, BodyPreset } from '../../data/bodyPresets';

interface BodyMorphingPanelProps {
  customParams: BodyCustomParams;
  onChange: (params: BodyCustomParams) => void;
  onSelectPreset: (preset: BodyPreset) => void;
}

export const BodyMorphingPanel: React.FC<BodyMorphingPanelProps> = ({
  customParams,
  onChange,
  onSelectPreset,
}) => {
  const [showAdvanced, setShowAdvanced] = useState<boolean>(false);

  const handleProportionChange = (key: keyof BodyCustomParams['proportions'], value: number) => {
    onChange({
      ...customParams,
      proportions: {
        ...customParams.proportions,
        [key]: value,
      },
    });
  };

  return (
    <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* 4 Presets Grid */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.65rem' }}>
          <span style={{ fontSize: '0.825rem', fontWeight: 700, color: 'var(--vfit-on-surface)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Chọn nhanh vóc dáng người mẫu chuẩn:
          </span>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--vfit-focus-ring)',
              fontSize: '0.775rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.25rem',
            }}
          >
            {showAdvanced ? '▲ Ẩn bớt số đo' : '⚙️ Tùy chỉnh số đo chi tiết (Blender MPFB)'}
          </button>
        </div>

        <div className="vfit-preset-grid">
          {BODY_PRESETS.map((preset) => {
            const isSelected = customParams.selectedPresetId === preset.id;
            return (
              <button
                key={preset.id}
                type="button"
                className={`vfit-preset-card ${isSelected ? 'selected' : ''}`}
                onClick={() => onSelectPreset(preset)}
                style={{
                  border: isSelected ? '2px solid var(--vfit-focus-ring)' : '1px solid var(--vfit-border-subtle)',
                }}
              >
                <img src={preset.img} alt={preset.name} />
                <div className="vfit-preset-overlay">
                  <span style={{ fontSize: '0.75rem', fontWeight: 800 }}>{preset.name}</span>
                  <span style={{ fontSize: '0.65rem', color: '#cbd5e1' }}>{preset.stats}</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Advanced Biometric Morphing Sliders (from body/BlenderTest) */}
      {showAdvanced && (
        <div
          style={{
            padding: '1.25rem',
            backgroundColor: 'var(--vfit-surface-container-low)',
            borderRadius: 'var(--vfit-radius-lg)',
            border: '1px solid var(--vfit-border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
            animation: 'vfitFadeIn 0.2s ease-out',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--vfit-primary-container)', letterSpacing: '0.05em' }}>
              🧬 Tham số giải phẫu cơ thể học 3D (MPFB2 Sliders)
            </span>
            <span style={{ fontSize: '0.7rem', color: 'var(--vfit-secondary)' }}>
              Đồng bộ trực tiếp với Blender 3D Engine
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.85rem' }}>
            {/* Height */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 600, color: 'var(--vfit-on-surface)' }}>
                <span>Chiều cao</span>
                <span style={{ color: 'var(--vfit-primary-container)', fontWeight: 800 }}>{customParams.height} cm</span>
              </div>
              <input
                type="range"
                min="145"
                max="205"
                value={customParams.height}
                onChange={(e) => onChange({ ...customParams, height: Number(e.target.value) })}
                style={{ width: '100%', accentColor: 'var(--vfit-primary-container)' }}
              />
            </div>

            {/* Weight */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 600, color: 'var(--vfit-on-surface)' }}>
                <span>Cân nặng</span>
                <span style={{ color: 'var(--vfit-primary-container)', fontWeight: 800 }}>{customParams.weight} kg</span>
              </div>
              <input
                type="range"
                min="40"
                max="110"
                value={customParams.weight}
                onChange={(e) => onChange({ ...customParams, weight: Number(e.target.value) })}
                style={{ width: '100%', accentColor: 'var(--vfit-primary-container)' }}
              />
            </div>

            {/* Shoulder Width */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 600, color: 'var(--vfit-on-surface)' }}>
                <span>Độ rộng vai</span>
                <span>{Math.round(customParams.proportions.shoulder_width * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={customParams.proportions.shoulder_width}
                onChange={(e) => handleProportionChange('shoulder_width', Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--vfit-focus-ring)' }}
              />
            </div>

            {/* Chest */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 600, color: 'var(--vfit-on-surface)' }}>
                <span>Vòng ngực (Chest)</span>
                <span>{Math.round(customParams.proportions.chest * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={customParams.proportions.chest}
                onChange={(e) => handleProportionChange('chest', Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--vfit-focus-ring)' }}
              />
            </div>

            {/* Waist */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 600, color: 'var(--vfit-on-surface)' }}>
                <span>Vòng eo (Waist)</span>
                <span>{Math.round(customParams.proportions.waist * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={customParams.proportions.waist}
                onChange={(e) => handleProportionChange('waist', Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--vfit-focus-ring)' }}
              />
            </div>

            {/* Hips */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 600, color: 'var(--vfit-on-surface)' }}>
                <span>Vòng hông (Hips)</span>
                <span>{Math.round(customParams.proportions.hips * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={customParams.proportions.hips}
                onChange={(e) => handleProportionChange('hips', Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--vfit-focus-ring)' }}
              />
            </div>

            {/* Muscle Tone */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 600, color: 'var(--vfit-on-surface)' }}>
                <span>Độ cơ bắp (Muscle Tone)</span>
                <span>{Math.round(customParams.proportions.muscle_tone * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={customParams.proportions.muscle_tone}
                onChange={(e) => handleProportionChange('muscle_tone', Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--vfit-focus-ring)' }}
              />
            </div>

            {/* Skin Tone */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 600, color: 'var(--vfit-on-surface)', marginBottom: '0.25rem' }}>
                <span>Sắc tố màu da</span>
                <span style={{ textTransform: 'capitalize' }}>{customParams.skinTone}</span>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                {[
                  { tone: 'light', color: '#F3D5B5', label: 'Sáng' },
                  { tone: 'medium', color: '#C68642', label: 'Tự nhiên' },
                  { tone: 'dark', color: '#8D5524', label: 'Ngăm' },
                ].map((s) => (
                  <button
                    key={s.tone}
                    type="button"
                    onClick={() =>
                      onChange({
                        ...customParams,
                        skinTone: s.tone as any,
                        skinColorHex: s.color,
                      })
                    }
                    style={{
                      flex: 1,
                      padding: '0.35rem',
                      borderRadius: 'var(--vfit-radius-sm)',
                      backgroundColor: s.color,
                      border: customParams.skinTone === s.tone ? '2px solid var(--vfit-primary-container)' : '1px solid rgba(0,0,0,0.1)',
                      fontSize: '0.7rem',
                      fontWeight: 700,
                      color: s.tone === 'dark' ? '#fff' : '#000',
                      cursor: 'pointer',
                    }}
                  >
                    {s.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
