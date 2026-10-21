import React, { useState } from 'react';
import { BodyParameters, defaultBodyParameters } from '../../api/bodyBuilderApi';

interface Props {
  onBack: () => void;
  onNext: (params: BodyParameters) => void;
  initialParams?: BodyParameters | null;
  submitLabel?: string;
  disabled?: boolean;
}

const defaults = defaultBodyParameters();

const PROPORTION_SLIDERS: { key: keyof BodyParameters['proportions']; label: string; icon: string }[] = [
  { key: 'shoulder_width', label: 'Bề rộng vai', icon: '🫱' },
  { key: 'chest', label: 'Ngực', icon: '💪' },
  { key: 'waist', label: 'Eo', icon: '⌛' },
  { key: 'hips', label: 'Hông', icon: '🔵' },
  { key: 'leg_length', label: 'Dài chân', icon: '🦵' },
  { key: 'arm_length', label: 'Dài tay', icon: '💪' },
  { key: 'muscle_tone', label: 'Cơ bắp', icon: '🏋️' },
  { key: 'belly', label: 'Bụng', icon: '🫃' },
  { key: 'buttocks', label: 'Mông', icon: '🍑' },
];

const PRESETS = [
  { label: 'Mặc định', params: () => defaults },
  { label: 'Nam cao', params: () => ({ ...defaults, height_cm: 180, weight_kg: 74, gender: 'male' as const }) },
  { label: 'Nữ chuẩn', params: () => ({ ...defaults, height_cm: 160, weight_kg: 54, gender: 'female' as const }) },
  { label: 'Đầy đặn', params: () => ({ ...defaults, height_cm: 165, weight_kg: 68, gender: 'female' as const, proportions: { ...defaults.proportions, hips: 0.7, waist: 0.65 } }) },
];

const Bs = {
  wrap: { display: 'flex', flexDirection: 'column' as const, gap: '1.25rem' } as React.CSSProperties,
  label: { fontSize: '.8rem', fontWeight: 700, color: '#677089', textTransform: 'uppercase' as const, letterSpacing: '.06em', marginBottom: 10, display: 'block' } as React.CSSProperties,

  /* basic info grid */
  basicGrid: { display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.85rem' } as React.CSSProperties,
  fieldBox: { background: '#f7f8fc', border: '1.5px solid #e4e7f0', borderRadius: 14, padding: '0.7rem 0.9rem', display: 'flex', flexDirection: 'column' as const, gap: 4 } as React.CSSProperties,
  fieldName: { fontSize: '.75rem', fontWeight: 700, color: '#8991aa', textTransform: 'uppercase' as const, letterSpacing: '.06em' } as React.CSSProperties,
  fieldRow: { display: 'flex', alignItems: 'center', gap: 6 } as React.CSSProperties,
  numberInput: { flex: 1, border: 'none', background: 'transparent', fontSize: '1.05rem', fontWeight: 700, color: '#172033', outline: 'none', width: 56 } as React.CSSProperties,
  fieldUnit: { fontSize: '.82rem', color: '#9aa0b2', fontWeight: 600 } as React.CSSProperties,

  selectFull: { width: '100%', border: 'none', background: 'transparent', fontSize: '1rem', fontWeight: 700, color: '#172033', outline: 'none', gridColumn: '1 / -1' } as React.CSSProperties,
  colorInput: { width: 36, height: 36, border: 'none', borderRadius: 8, cursor: 'pointer', padding: 0, background: 'none' } as React.CSSProperties,

  /* presets */
  presetRow: { display: 'flex', gap: 8, flexWrap: 'wrap' as const } as React.CSSProperties,
  presetChip: (active: boolean): React.CSSProperties => ({
    padding: '5px 14px', borderRadius: 999, fontSize: '.8rem', fontWeight: 700, cursor: 'pointer',
    border: '1.5px solid',
    borderColor: active ? '#5a46d7' : '#dde1ef',
    background: active ? '#eef0ff' : '#fff',
    color: active ? '#4a39c7' : '#677089',
    transition: 'all .15s',
  }),

  /* slider section */
  sliderGrid: { display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.9rem 1.5rem' } as React.CSSProperties,
  sliderRow: { display: 'flex', flexDirection: 'column' as const, gap: 4 } as React.CSSProperties,
  sliderHead: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' } as React.CSSProperties,
  sliderLabel: { fontSize: '.8rem', fontWeight: 600, color: '#4f586d' } as React.CSSProperties,
  sliderVal: { fontSize: '.78rem', fontWeight: 800, color: '#4a39c7', background: '#eef0ff', padding: '2px 7px', borderRadius: 6 } as React.CSSProperties,

  /* divider */
  divider: { border: 'none', borderTop: '1.5px solid #f0f1f6', margin: '0.25rem 0' } as React.CSSProperties,

  /* actions */
  actions: { display: 'flex', gap: 10, paddingTop: 4 } as React.CSSProperties,
  btnBack: { padding: '0.65rem 1.1rem', borderRadius: 12, border: '1.5px solid #dde1ef', background: '#fff', color: '#4a39c7', fontWeight: 700, fontSize: '.88rem', cursor: 'pointer' } as React.CSSProperties,
  btnNext: { flex: 1, padding: '0.75rem', borderRadius: 12, border: 'none', background: 'linear-gradient(135deg,#5a46d7,#3b82f6)', color: '#fff', fontWeight: 800, fontSize: '.95rem', cursor: 'pointer' } as React.CSSProperties,
};

export const BodyBuilderStep: React.FC<Props> = ({ onBack, onNext, initialParams, submitLabel, disabled = false }) => {
  const [params, setParams] = useState<BodyParameters>(initialParams || defaults);
  const [activePreset, setActivePreset] = useState<number | null>(0);

  const setNumber = (key: 'height_cm' | 'weight_kg' | 'age', value: number) => {
    setActivePreset(null);
    setParams((cur) => ({ ...cur, [key]: value }));
  };

  const applyPreset = (index: number) => {
    setActivePreset(index);
    setParams(PRESETS[index].params());
  };

  const canSubmit = !disabled
    && params.height_cm >= 140 && params.height_cm <= 210
    && params.weight_kg >= 35 && params.weight_kg <= 150
    && params.age >= 10 && params.age <= 80
    && params.measurements_cm.shoulder_width_cm >= 30 && params.measurements_cm.shoulder_width_cm <= 65
    && params.measurements_cm.chest_cm >= 55 && params.measurements_cm.chest_cm <= 160
    && params.measurements_cm.waist_cm >= 45 && params.measurements_cm.waist_cm <= 150
    && params.measurements_cm.hip_cm >= 60 && params.measurements_cm.hip_cm <= 170
    && params.measurements_cm.inseam_cm >= 50 && params.measurements_cm.inseam_cm <= 115;

  return (
    <div style={Bs.wrap}>

      {/* ── Mẫu nhanh ── */}
      <div>
        <span style={Bs.label}>Mẫu nhanh</span>
        <div style={Bs.presetRow}>
          {PRESETS.map((p, i) => (
            <button key={p.label} type="button" style={Bs.presetChip(activePreset === i)}
              onClick={() => applyPreset(i)} disabled={disabled}>
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <hr style={Bs.divider} />

      {/* ── Thông số cơ bản ── */}
      <div>
        <span style={Bs.label}>Thông số cơ bản</span>
        <div style={Bs.basicGrid}>
          {/* Height */}
          <div style={Bs.fieldBox}>
            <span style={Bs.fieldName}>Chiều cao</span>
            <div style={Bs.fieldRow}>
              <input type="number" min={140} max={210} value={params.height_cm} disabled={disabled}
                onChange={(e) => setNumber('height_cm', Number(e.target.value))} style={Bs.numberInput} />
              <span style={Bs.fieldUnit}>cm</span>
            </div>
          </div>
          {/* Weight */}
          <div style={Bs.fieldBox}>
            <span style={Bs.fieldName}>Cân nặng</span>
            <div style={Bs.fieldRow}>
              <input type="number" min={35} max={150} value={params.weight_kg} disabled={disabled}
                onChange={(e) => setNumber('weight_kg', Number(e.target.value))} style={Bs.numberInput} />
              <span style={Bs.fieldUnit}>kg</span>
            </div>
          </div>
          {/* Age */}
          <div style={Bs.fieldBox}>
            <span style={Bs.fieldName}>Tuổi</span>
            <div style={Bs.fieldRow}>
              <input type="number" min={10} max={80} value={params.age} disabled={disabled}
                onChange={(e) => setNumber('age', Number(e.target.value))} style={Bs.numberInput} />
              <span style={Bs.fieldUnit}>tuổi</span>
            </div>
          </div>
          {/* Skin color */}
          <div style={Bs.fieldBox}>
            <span style={Bs.fieldName}>Màu da</span>
            <div style={Bs.fieldRow}>
              <input type="color" value={params.skin_color} disabled={disabled}
                onChange={(e) => { setActivePreset(null); setParams({ ...params, skin_color: e.target.value }); }}
                style={Bs.colorInput} />
              <span style={{ ...Bs.fieldUnit, fontSize: '.75rem', fontFamily: 'monospace' }}>{params.skin_color.toUpperCase()}</span>
            </div>
          </div>
          {/* Gender - full width */}
          <div style={{ ...Bs.fieldBox, gridColumn: '1 / -1' }}>
            <span style={Bs.fieldName}>Giới tính</span>
            <select value={params.gender} disabled={disabled} style={Bs.selectFull}
              onChange={(e) => { setActivePreset(null); setParams({ ...params, gender: e.target.value as BodyParameters['gender'] }); }}>
              <option value="neutral">Trung tính (mẫu Blender)</option>
              <option value="female">Nữ</option>
              <option value="male">Nam</option>
            </select>
          </div>
        </div>
      </div>

      <hr style={Bs.divider} />

      {/* ── Tỷ lệ hình thể ── */}
      <div>
        <span style={Bs.label}>Tỷ lệ hình thể <span style={{ color: '#b8bdd4', fontWeight: 400, textTransform: 'none', fontSize: '.75rem', letterSpacing: 0 }}>(điều chỉnh dáng người, không phải số đo)</span></span>
        <div style={Bs.sliderGrid}>
          <div style={{ gridColumn: '1 / -1', fontSize: '.8rem', fontWeight: 700, color: '#677089' }}>
            Số đo mục tiêu ước lượng (cm)
          </div>
          {([
            ['shoulder_width_cm', 'Rộng vai', 30, 65],
            ['chest_cm', 'Vòng ngực', 55, 160],
            ['waist_cm', 'Vòng eo', 45, 150],
            ['hip_cm', 'Vòng hông', 60, 170],
            ['inseam_cm', 'Dài chân trong', 50, 115],
          ] as const).map(([key, label, min, max]) => (
            <label key={key} style={Bs.fieldBox}>
              <span style={Bs.fieldName}>{label}</span>
              <div style={Bs.fieldRow}>
                <input type="number" min={min} max={max} step={0.5}
                  value={params.measurements_cm[key]} disabled={disabled}
                  onChange={(e) => {
                    setActivePreset(null);
                    setParams((cur) => ({
                      ...cur,
                      measurements_cm: { ...cur.measurements_cm, [key]: Number(e.target.value) },
                    }));
                  }} style={Bs.numberInput} />
                <span style={Bs.fieldUnit}>cm</span>
              </div>
            </label>
          ))}
          <div style={{ gridColumn: '1 / -1', fontSize: '.75rem', color: '#8991aa' }}>
            MPFB dùng các giá trị này để ước lượng dáng body; đây không phải số đo xác minh từ ảnh.
          </div>
          {PROPORTION_SLIDERS.filter(({ key }) => ![
            'shoulder_width', 'chest', 'waist', 'hips', 'leg_length',
          ].includes(key)).map(({ key, label, icon }) => {
            const pct = Math.round(params.proportions[key] * 100);
            return (
              <div key={key} style={Bs.sliderRow}>
                <div style={Bs.sliderHead}>
                  <span style={Bs.sliderLabel}>{icon} {label}</span>
                  <span style={Bs.sliderVal}>{pct}%</span>
                </div>
                <input type="range" min={0} max={100} value={pct} disabled={disabled}
                  style={{ width: '100%', accentColor: '#5a46d7', height: 4 }}
                  onChange={(e) => {
                    setActivePreset(null);
                    setParams((cur) => ({
                      ...cur,
                      proportions: { ...cur.proportions, [key]: Number(e.target.value) / 100 },
                    }));
                  }} />
              </div>
            );
          })}
        </div>
      </div>

      <hr style={Bs.divider} />

      {/* ── Actions ── */}
      <div style={Bs.actions}>
        <button type="button" style={Bs.btnBack} disabled={disabled} onClick={onBack}>← Quay lại</button>
        <button type="button" style={{ ...Bs.btnNext, opacity: canSubmit ? 1 : .5, cursor: canSubmit ? 'pointer' : 'not-allowed' }}
          disabled={!canSubmit} onClick={() => onNext(params)}>
          {disabled ? '⏳ Đang xử lý…' : (submitLabel || '🏗️ Tạo body MPFB →')}
        </button>
      </div>

    </div>
  );
};
