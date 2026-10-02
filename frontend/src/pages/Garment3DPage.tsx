import React, { FormEvent, useState } from 'react';
import { GarmentImageSet } from '../api/garment3d';
import { GarmentGenerationProgress } from '../components/GarmentGenerationProgress';
import { GarmentFiles, GarmentImageInputs } from '../components/GarmentImageInputs';
import { useGarmentGeneration } from '../hooks/useGarmentGeneration';
import { Garment360Viewer } from '../viewer/Garment360Viewer';

export const Garment3DPage: React.FC = () => {
  const [files, setFiles] = useState<GarmentFiles>({});
  const { job, generation, error, submitting, submit, reset } = useGarmentGeneration();

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!files.front) return;
    void submit(files as GarmentImageSet);
  };

  const startAgain = () => {
    reset();
    setFiles({});
  };

  return (
    <main className="g3d-app">
      <header className="g3d-hero">
        <div>
          <span className="g3d-hero__pill">AI Garment Studio</span>
          <h1>Biến ảnh trang phục thành mô hình 3D</h1>
          <p>
            Tải lên từ một đến bốn góc ảnh. Hệ thống sẽ tự chuẩn hóa và tạo mesh có thể xem
            360° ngay trên trình duyệt.
          </p>
        </div>
        <div className="g3d-hero__orb" aria-hidden="true">360°</div>
      </header>

      {!generation && (
        <form className="g3d-form" onSubmit={onSubmit}>
          <GarmentImageInputs files={files} onChange={setFiles} disabled={submitting || !!job} />
          {!job && (
            <div className="g3d-submit-row">
              <p>Ảnh mặt trước càng rõ, kết quả càng chính xác.</p>
              <button
                className="g3d-button g3d-button--primary"
                type="submit"
                disabled={!files.front || submitting}
              >
                {submitting ? 'Đang tải ảnh…' : 'Tạo mô hình 3D'}
              </button>
            </div>
          )}
        </form>
      )}

      {job && !generation && <GarmentGenerationProgress job={job} />}
      {error && (
        <div className="g3d-alert" role="alert">
          <p>{error}</p>
          <button className="g3d-button g3d-button--secondary" type="button" onClick={startAgain}>
            Thử lại
          </button>
        </div>
      )}
      {generation?.assets && (
        <section className="g3d-panel g3d-result">
          <div className="g3d-section-heading">
            <div>
              <span className="g3d-eyebrow">Hoàn tất</span>
              <h2>Mô hình 3D của bạn</h2>
            </div>
          </div>
          <Garment360Viewer
            modelUrl={generation.assets.glb_url}
            thumbnailUrl={generation.assets.thumbnail_url}
          />
          <div className="g3d-result__footer">
            <p>Kéo để xoay 360°, cuộn hoặc chụm để zoom.</p>
            <button className="g3d-button g3d-button--secondary" type="button" onClick={startAgain}>
              Tạo mô hình khác
            </button>
          </div>
        </section>
      )}
    </main>
  );
};
