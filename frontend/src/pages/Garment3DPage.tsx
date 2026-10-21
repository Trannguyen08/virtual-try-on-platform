import React, { FormEvent, useState } from 'react';
import { GarmentImageSet, GarmentType } from '../api/garment3d';
import { GarmentGenerationProgress } from '../components/GarmentGenerationProgress';
import { GarmentFiles, GarmentImageInputs } from '../components/GarmentImageInputs';
import { SizeChartPanel } from '../components/SizeChartPanel';
import { useGarmentGeneration } from '../hooks/useGarmentGeneration';
import { GarmentSize, getGarmentSizeProfile, SizeRegion } from '../data/sizeCharts';
import { Garment360Viewer } from '../viewer/Garment360Viewer';
import { buildGarmentAnnotations } from '../viewer/garmentAnnotations';

const GARMENT_TYPE_LABELS: Record<string, string> = {
  tshirt: 'Áo thun (T-shirt)',
  shirt: 'Áo sơ mi (Shirt)',
  jacket: 'Áo khoác (Jacket)',
  pants: 'Quần dài (Pants)',
  skirt: 'Chân váy (Skirt)',
  dress: 'Đầm/Váy liền (Dress)',
};

export const Garment3DPage: React.FC = () => {
  const [files, setFiles] = useState<GarmentFiles>({});
  const [sizeRegion, setSizeRegion] = useState<SizeRegion>('asia');
  const [selectedSize, setSelectedSize] = useState<GarmentSize>('M');
  const { job, generation, error, submitting, submit, reset } = useGarmentGeneration();

  const resolvedGarmentType: GarmentType =
    (generation?.garment?.garment_type as GarmentType) || 'tshirt';

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!files.front) return;
    void submit(files as GarmentImageSet, {
      garmentType: 'auto',
    });
  };

  const startAgain = () => {
    reset();
    setFiles({});
    setSizeRegion('asia');
    setSelectedSize('M');
  };

  const sizeProfiles = getGarmentSizeProfile(resolvedGarmentType, sizeRegion);
  const selectedProfile = sizeProfiles[selectedSize] ?? sizeProfiles.M;
  const mediumProfile = sizeProfiles.M;
  const sizeScale: [number, number, number] = [
    selectedProfile.widthCm / mediumProfile.widthCm,
    selectedProfile.lengthCm / mediumProfile.lengthCm,
    selectedProfile.widthCm / mediumProfile.widthCm,
  ];

  return (
    <div className="g3d-app">
      <header className="g3d-hero">
        <div>
          <span className="g3d-hero__pill">Garment 3D Studio</span>
          <h1>Biến ảnh trang phục thành mô hình 3D</h1>
          <p>
            Tải lên từ một đến bốn góc ảnh. Hệ thống tự động tách nền, nhận diện loại trang phục
            và tạo mesh 3D có thể xem 360° ngay trên trình duyệt.
          </p>
        </div>
        <div className="g3d-hero__orb" aria-hidden="true">360°</div>
      </header>

      <form className="g3d-form" onSubmit={onSubmit}>
        <GarmentImageInputs files={files} onChange={setFiles} disabled={submitting || !!job} />
        {!job && (
          <div className="g3d-submit-row">
            <p>Hệ thống tự động tách nền, nhận diện loại trang phục và tạo mesh 3D.</p>
            <button
              className="g3d-button g3d-button--primary"
              type="submit"
              disabled={!files.front || submitting}
            >
              {submitting ? 'Đang phân tích & tải ảnh…' : 'Tạo mô hình 3D (Tự động nhận diện)'}
            </button>
          </div>
        )}
      </form>

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
              <span className="g3d-eyebrow">
                Tự động nhận diện: {GARMENT_TYPE_LABELS[resolvedGarmentType] || resolvedGarmentType}
              </span>
              <h2>Mô hình 3D của bạn</h2>
            </div>
          </div>
          {generation.assets.thumbnail_url && (
            <figure className="g3d-processed-preview">
              <img src={generation.assets.thumbnail_url} alt="Trang phục sau khi tách nền" />
              <figcaption>Kết quả tách nền dùng để dựng mesh</figcaption>
            </figure>
          )}
          <Garment360Viewer
            modelUrl={generation.assets.glb_url}
            thumbnailUrl={generation.assets.thumbnail_url}
            scale={sizeScale}
            annotations={buildGarmentAnnotations(
              resolvedGarmentType,
              generation.garment?.landmarks,
            )}
          />
          <SizeChartPanel
            garmentType={resolvedGarmentType}
            region={sizeRegion}
            size={selectedSize}
            onRegionChange={setSizeRegion}
            onSizeChange={setSelectedSize}
          />
          {generation.garment && (
            <section className="g3d-measurements" aria-labelledby="garment-measurements-title">
              <div className="g3d-section-heading">
                <div>
                  <span className="g3d-eyebrow">
                    {generation.garment.fit_ready ? 'Sẵn sàng ghép body' : 'Kích thước tham chiếu'}
                  </span>
                  <h3 id="garment-measurements-title">Thông số trang phục</h3>
                </div>
              </div>
              <div className="g3d-measurement-grid">
                {Object.entries(generation.garment.measurements).map(([name, measurement]) => (
                  <article key={name} className="g3d-measurement-card">
                    <span>{name.replaceAll('_', ' ')}</span>
                    <strong>
                      {measurement.value_cm !== null
                        ? `${measurement.value_cm.toFixed(1)} cm`
                        : `${measurement.value_px.toFixed(0)} px`}
                    </strong>
                    <small>Độ tin cậy {Math.round(measurement.confidence * 100)}%</small>
                  </article>
                ))}
              </div>
            </section>
          )}
          <div className="g3d-result__footer">
            <p>Kéo để xoay 360°, cuộn hoặc chụm để zoom.</p>
            <div className="g3d-downloads">
              <a className="g3d-button g3d-button--primary" href={generation.assets.glb_url} download>
                Tải GLB
              </a>
              {generation.assets.metadata_url && (
                <a
                  className="g3d-button g3d-button--secondary"
                  href={generation.assets.metadata_url}
                  download
                >
                  Tải thông số JSON
                </a>
              )}
            </div>
            <button className="g3d-button g3d-button--secondary" type="button" onClick={startAgain}>
              Tạo mô hình khác
            </button>
          </div>
        </section>
      )}
    </div>
  );
};

export default Garment3DPage;
