import React, { FormEvent, useState } from 'react';
import { GarmentImageSet, GarmentType } from '../api/garment3d';
import { GarmentGenerationProgress } from '../components/GarmentGenerationProgress';
import { GarmentFiles, GarmentImageInputs } from '../components/GarmentImageInputs';
import { SizeChartPanel } from '../components/SizeChartPanel';
import { useGarmentGeneration } from '../hooks/useGarmentGeneration';
import { GarmentSize, getGarmentSizeProfile, SizeRegion } from '../data/sizeCharts';
import { Garment360Viewer } from '../viewer/Garment360Viewer';
import { buildGarmentAnnotations } from '../viewer/garmentAnnotations';

export const Garment3DPage: React.FC = () => {
  const [files, setFiles] = useState<GarmentFiles>({});
  const [garmentType, setGarmentType] = useState<GarmentType>('tshirt');
  const [sizeRegion, setSizeRegion] = useState<SizeRegion>('asia');
  const [selectedSize, setSelectedSize] = useState<GarmentSize>('M');
  const [referenceValue, setReferenceValue] = useState('');
  const { job, generation, error, submitting, submit, reset } = useGarmentGeneration();

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!files.front) return;
    const parsedReference = Number(referenceValue);
    void submit(files as GarmentImageSet, {
      garmentType,
      referenceMeasurement: parsedReference > 0 ? 'garment_length' : undefined,
      referenceValueCm: parsedReference > 0 ? parsedReference : undefined,
    });
  };

  const startAgain = () => {
    reset();
    setFiles({});
    setGarmentType('tshirt');
    setSizeRegion('asia');
    setSelectedSize('M');
    setReferenceValue('');
  };

  const sizeProfiles = getGarmentSizeProfile(garmentType, sizeRegion);
  const selectedProfile = sizeProfiles[selectedSize];
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
            Tải lên từ một đến bốn góc ảnh. Hệ thống sẽ tự chuẩn hóa và tạo mesh có thể xem
            360° ngay trên trình duyệt.
          </p>
        </div>
        <div className="g3d-hero__orb" aria-hidden="true">360°</div>
      </header>

      <form className="g3d-form" onSubmit={onSubmit}>
          <GarmentImageInputs files={files} onChange={setFiles} disabled={submitting || !!job} />
          <section className="g3d-panel g3d-calibration" aria-labelledby="garment-scale-title">
            <div className="g3d-section-heading">
              <div>
                <span className="g3d-eyebrow">Bước 2</span>
                <h2 id="garment-scale-title">Loại đồ và kích thước thật</h2>
              </div>
            </div>
            <div className="g3d-field-grid">
              <label className="g3d-field">
                <span>Loại trang phục</span>
                <select
                  value={garmentType}
                  disabled={submitting || !!job}
                  onChange={(event) => setGarmentType(event.target.value as GarmentType)}
                >
                  <option value="tshirt">Áo thun</option>
                  <option value="shirt">Áo sơ mi</option>
                  <option value="jacket">Áo khoác</option>
                  <option value="pants">Quần dài</option>
                  <option value="skirt">Chân váy</option>
                  <option value="dress">Váy liền</option>
                </select>
              </label>
              <label className="g3d-field">
                <span>Chiều dài trang phục thực tế (cm)</span>
                <input
                  type="number"
                  min="1"
                  max="300"
                  step="0.1"
                  inputMode="decimal"
                  value={referenceValue}
                  disabled={submitting || !!job}
                  placeholder="Ví dụ: 68"
                  onChange={(event) => setReferenceValue(event.target.value)}
                />
              </label>
            </div>
            <p className="g3d-section-copy">
              Số đo này dùng để đổi pixel sang centimet. Nếu bỏ trống, mô hình vẫn xem được
              nhưng chưa đủ tin cậy để ghép theo kích thước body.
            </p>
          </section>
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
              garmentType,
              generation.garment?.landmarks,
            )}
          />
          <SizeChartPanel
            garmentType={garmentType}
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
                    {generation.garment.fit_ready ? 'Sẵn sàng ghép body' : 'Chưa hiệu chỉnh cm'}
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
