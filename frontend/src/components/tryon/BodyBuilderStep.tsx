import React, { useState } from 'react';
import { BodyParameters, defaultBodyParameters } from '../../api/bodyBuilderApi';

interface Props {
  onBack: () => void;
  onNext: (params: BodyParameters) => void;
  initialParams?: BodyParameters | null;
  disabled?: boolean;
}

const defaults = defaultBodyParameters();

const sliders: { key: keyof BodyParameters['proportions']; label: string }[] = [
  { key: 'shoulder_width', label: 'Vai' }, { key: 'chest', label: 'Ngực' },
  { key: 'waist', label: 'Eo' }, { key: 'hips', label: 'Hông' },
  { key: 'leg_length', label: 'Chiều dài chân' }, { key: 'arm_length', label: 'Chiều dài tay' },
  { key: 'muscle_tone', label: 'Cơ bắp' }, { key: 'belly', label: 'Bụng' },
  { key: 'buttocks', label: 'Mông' },
];

export const BodyBuilderStep: React.FC<Props> = ({ onBack, onNext, initialParams, disabled = false }) => {
  const [params, setParams] = useState<BodyParameters>(initialParams || defaults);
  const setNumber = (key: 'height_cm' | 'weight_kg' | 'age', value: number) =>
    setParams((current) => ({ ...current, [key]: value }));

  return (
    <div className="vfit-builder-layout">
      <section className="vfit-builder-card">
        <span className="vfit-builder-eyebrow">Bước 1 • Dựng body với Blender</span>
        <h2>Tạo body 3D từ thông số</h2>
        <p>Điều chỉnh tỷ lệ, tạo GLB và xem ngay trên giao diện thử đồ. Các thanh tỷ lệ là điều khiển hình dáng, không phải số đo cơ thể.</p>
        <div className="vfit-builder-fields">
          {([
            ['height_cm', 'Chiều cao', 140, 210, 'cm'],
            ['weight_kg', 'Cân nặng', 35, 150, 'kg'],
            ['age', 'Tuổi', 10, 80, ''],
          ] as const).map(([key, label, min, max, unit]) => (
            <label key={key}>{label}
              <span><input type="number" min={min} max={max} value={params[key]}
                onChange={(event) => setNumber(key, Number(event.target.value))} /> {unit}</span>
            </label>
          ))}
          <label>Giới tính
            <select value={params.gender} onChange={(event) => setParams({ ...params, gender: event.target.value as BodyParameters['gender'] })}>
              <option value="neutral">Trung tính (mẫu Blender)</option>
              <option value="female">Nữ</option><option value="male">Nam</option>
            </select>
          </label>
          <label>Màu da
            <input type="color" value={params.skin_color}
              onChange={(event) => setParams({ ...params, skin_color: event.target.value })} />
          </label>
        </div>
        <div className="vfit-builder-presets">
          <span>Tỷ lệ mẫu</span>
          <button type="button" onClick={() => setParams(defaults)}>Mặc định</button>
          <button type="button" onClick={() => setParams({ ...defaults, height_cm: 180, weight_kg: 74, gender: 'male' })}>Nam cao</button>
          <button type="button" onClick={() => setParams({ ...defaults, height_cm: 165, weight_kg: 68,
            proportions: { ...defaults.proportions, hips: 0.7, waist: 0.65 } })}>Đầy đặn</button>
        </div>
        <div className="vfit-builder-actions">
          <button className="vfit-btn-secondary" type="button" disabled={disabled} onClick={onBack}>← Quay lại</button>
          <button className="vfit-btn-primary" type="button"
            disabled={disabled || params.height_cm < 140 || params.height_cm > 210 || params.weight_kg < 35 || params.weight_kg > 150 || params.age < 10 || params.age > 80}
            onClick={() => onNext(params)}>Tạo body MPFB →</button>
        </div>
      </section>
      <section className="vfit-builder-card">
        <h3>Tỷ lệ body</h3>
        <div className="vfit-builder-sliders">
          {sliders.map(({ key, label }) => (
            <label key={key}><span>{label} <strong>{Math.round(params.proportions[key] * 100)}%</strong></span>
              <input type="range" min="0" max="100" value={Math.round(params.proportions[key] * 100)}
                onChange={(event) => setParams((current) => ({ ...current,
                  proportions: { ...current.proportions, [key]: Number(event.target.value) / 100 },
                }))} />
            </label>
          ))}
        </div>
        <p className="vfit-builder-note">Body được dựng bằng MPFB2 trong Blender. Nếu add-on chưa hoạt động, hệ thống báo lỗi để bạn kiểm tra cấu hình.</p>
      </section>
    </div>
  );
};
