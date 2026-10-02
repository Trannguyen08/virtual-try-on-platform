import React from 'react';
import { Garment3DJob } from '../api/garment3d';

const LABELS: Record<string, string> = {
  validating: 'Đang kiểm tra ảnh',
  uploading: 'Đang tải ảnh lên',
  queued: 'Đang chuẩn bị tạo mô hình',
  generating: 'Đang tạo hình học và texture 3D',
  downloading: 'Đang tải mô hình',
  postprocessing: 'Đang tối ưu mô hình',
  validating_mesh: 'Đang kiểm tra mesh',
  completed: 'Mô hình đã sẵn sàng',
  failed: 'Tạo mô hình thất bại',
  cancelled: 'Đã hủy',
};

export const GarmentGenerationProgress: React.FC<{ job: Garment3DJob }> = ({ job }) => (
  <section
    className="g3d-panel g3d-progress"
    aria-live="polite"
    aria-busy={job.status !== 'completed'}
  >
    <div className="g3d-progress__header">
      <div>
        <span className="g3d-eyebrow">Đang xử lý</span>
        <h2>{LABELS[job.status] ?? 'Đang xử lý'}</h2>
      </div>
      <strong>{job.progress}%</strong>
    </div>
    <progress max={100} value={job.progress}>{job.progress}%</progress>
    {job.warnings.includes('BACK_AND_SIDES_INFERRED_FROM_SINGLE_IMAGE') && (
      <p className="g3d-warning">Mặt bên và mặt sau đang được AI suy đoán từ một ảnh.</p>
    )}
  </section>
);
