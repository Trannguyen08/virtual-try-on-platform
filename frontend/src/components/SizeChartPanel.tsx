import React from 'react';
import { GarmentType } from '../api/garment3d';
import { GarmentSize, getGarmentSizeProfile, SizeRegion } from '../data/sizeCharts';

const SIZE_OPTIONS: GarmentSize[] = ['S', 'M', 'L', 'XL', 'XXL'];

const REGION_LABELS: Record<SizeRegion, string> = {
  asia: 'Châu Á',
  europe: 'Châu Âu',
};

export const SizeChartPanel: React.FC<{
  garmentType: GarmentType;
  region: SizeRegion;
  size: GarmentSize;
  onRegionChange: (region: SizeRegion) => void;
  onSizeChange: (size: GarmentSize) => void;
}> = ({ garmentType, region, size, onRegionChange, onSizeChange }) => {
  const profiles = getGarmentSizeProfile(garmentType, region);
  if (!profiles) return <p className="g3d-size-note" role="status">Chưa xác định loại trang phục để hiển thị bảng size tham khảo.</p>;
  const profile = profiles[size];

  return (
    <section className="g3d-size-chart" aria-labelledby="g3d-size-chart-title">
      <div className="g3d-section-heading">
        <div>
          <span className="g3d-eyebrow">Bảng size tham khảo</span>
          <h3 id="g3d-size-chart-title">Chọn khu vực và kích cỡ</h3>
        </div>
        <label className="g3d-size-region">
          <span>Khu vực size</span>
          <select
            value={region}
            onChange={(event) => onRegionChange(event.target.value as SizeRegion)}
          >
            {(Object.keys(REGION_LABELS) as SizeRegion[]).map((key) => (
              <option value={key} key={key}>{REGION_LABELS[key]}</option>
            ))}
          </select>
        </label>
      </div>

      <div className="g3d-size-options" role="group" aria-label="Chọn cỡ trang phục">
        {SIZE_OPTIONS.map((option) => (
          <button
            key={option}
            type="button"
            className={`g3d-size-option${size === option ? ' g3d-size-option--active' : ''}`}
            aria-pressed={size === option}
            onClick={() => onSizeChange(option)}
          >
            {option}
          </button>
        ))}
      </div>

      <div className="g3d-size-measurements">
        {profile.measurements.map((measurement) => (
          <article key={measurement.label} className="g3d-measurement-card">
            <span>{measurement.label}</span>
            <strong>{measurement.valueCm.toFixed(1)} cm</strong>
          </article>
        ))}
      </div>
      <p className="g3d-size-note">
        Đây là bảng tham khảo theo khu vực và loại trang phục, không phải chuẩn chung cho mọi thương hiệu.
        Số đo ngang được tính khi đặt phẳng. Mesh 3D co giãn tương đối theo bảng này, không phải số đo chính xác suy ra từ ảnh.
      </p>
    </section>
  );
};
