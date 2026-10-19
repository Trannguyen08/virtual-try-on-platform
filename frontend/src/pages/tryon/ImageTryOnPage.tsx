import React, { FormEvent, useCallback, useEffect, useRef, useState } from 'react';
import { bodyBuilderApi, BodyBuilderJob, BodyParameters } from '../../api/bodyBuilderApi';
import { GarmentType } from '../../api/garment3d';
import { imageTryOnApi, ImageTryOnJob } from '../../api/imageTryOnApi';
import { GarmentFiles, GarmentImageInputs } from '../../components/GarmentImageInputs';
import { BodyBuilderStep } from '../../components/tryon/BodyBuilderStep';
import { Product } from '../../data/mockProducts';
import { Garment360Viewer } from '../../viewer/Garment360Viewer';

const BODY_KEY = 'tryon.mpfb.body_id';
const JOB_KEY = 'tryon.image.job_id';
const GARMENT_TYPES: GarmentType[] = ['tshirt', 'shirt', 'jacket', 'pants', 'skirt', 'dress'];

function initialType(product?: Product | null): GarmentType {
  const category = product?.category === 't_shirt' ? 'tshirt' : product?.category;
  return GARMENT_TYPES.find((candidate) => candidate === category) ?? 'tshirt';
}

interface Props {
  initialGarment?: Product | null;
  onNavigateCatalog?: () => void;
}

export const ImageTryOnPage: React.FC<Props> = ({ initialGarment }) => {
  const [body, setBody] = useState<BodyBuilderJob | null>(null);
  const [existingBodyId, setExistingBodyId] = useState('');
  const [editingBody, setEditingBody] = useState(false);
  const [creatingBody, setCreatingBody] = useState(false);
  const [files, setFiles] = useState<GarmentFiles>({});
  const [garmentType, setGarmentType] = useState<GarmentType>(() => initialType(initialGarment));
  const [garmentLength, setGarmentLength] = useState('');
  const [job, setJob] = useState<ImageTryOnJob | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const controllerRef = useRef<AbortController | null>(null);

  const poll = useCallback(async (jobId: string, controller: AbortController) => {
    const deadline = Date.now() + 20 * 60 * 1000;
    while (!controller.signal.aborted && Date.now() < deadline) {
      const current = await imageTryOnApi.get(jobId, controller.signal);
      setJob(current);
      if (current.status === 'completed') return;
      if (current.status === 'failed') {
        window.localStorage.removeItem(JOB_KEY);
        setError(`${current.error?.code || 'PROCESSING_FAILED'}: ${current.error?.message || 'Không thể thử đồ'}`);
        return;
      }
      await new Promise<void>((resolve) => window.setTimeout(resolve, 2500));
    }
    if (!controller.signal.aborted) setError('Hết thời gian chờ. Bạn có thể tải lại trang để tiếp tục theo dõi job.');
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    controllerRef.current = controller;
    const savedBodyId = window.localStorage.getItem(BODY_KEY);
    const savedJobId = window.localStorage.getItem(JOB_KEY);
    if (savedBodyId) {
      void bodyBuilderApi.getBody(savedBodyId).then(setBody).catch(() => {
        window.localStorage.removeItem(BODY_KEY);
      });
    }
    if (savedJobId) {
      void poll(savedJobId, controller).catch((reason) => {
        if (!controller.signal.aborted) {
          setError(reason instanceof Error ? reason.message : 'Không thể kiểm tra job');
        }
      });
    }
    return () => controller.abort();
  }, [poll]);

  const createBody = async (parameters: BodyParameters) => {
    setCreatingBody(true);
    setError('');
    try {
      const created = await bodyBuilderApi.generate(parameters);
      const bodyId = created.body_id || created.job_id;
      setBody(created);
      setExistingBodyId(bodyId);
      setEditingBody(false);
      setJob(null);
      window.localStorage.setItem(BODY_KEY, bodyId);
      window.localStorage.removeItem(JOB_KEY);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không thể tạo body MPFB');
    } finally {
      setCreatingBody(false);
    }
  };

  const useExistingBody = async () => {
    setError('');
    try {
      const restored = await bodyBuilderApi.getBody(existingBodyId.trim());
      setBody(restored);
      setEditingBody(false);
      setJob(null);
      window.localStorage.setItem(BODY_KEY, existingBodyId.trim());
      window.localStorage.removeItem(JOB_KEY);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không tìm thấy body MPFB');
    }
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!body || !files.front) return;
    const length = Number(garmentLength);
    if (!Number.isFinite(length) || length < 1 || length > 300) {
      setError('Nhập chiều dài trang phục thật từ 1 đến 300 cm.');
      return;
    }
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setSubmitting(true);
    setError('');
    setJob(null);
    try {
      const created = await imageTryOnApi.create(
        body.body_id || body.job_id,
        { ...files, front: files.front }, garmentType, length, controller.signal,
      );
      setJob(created);
      window.localStorage.setItem(JOB_KEY, created.job_id);
      setSubmitting(false);
      await poll(created.job_id, controller);
    } catch (reason) {
      if (!controller.signal.aborted) {
        setError(reason instanceof Error ? reason.message : 'Không thể gửi ảnh trang phục');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const active = submitting || job?.status === 'pending' || job?.status === 'running';
  const result = job?.status === 'completed' ? job.result : null;

  return (
    <div className="vfit-image-tryon">
      <header className="vfit-builder-card">
        <h1>Thử trang phục từ ảnh trên body MPFB</h1>
        <p>Tạo hoặc chọn body đã có, tải ảnh cùng một trang phục và nhập chiều dài thật để dựng cảnh 3D.</p>
      </header>

      <section className="vfit-builder-card" aria-labelledby="tryon-body-title">
        <h2 id="tryon-body-title">1. Body MPFB</h2>
        {body && (
          <div>
            <p>Body đã chọn: <strong>{body.body_id || body.job_id}</strong></p>
            <a href={bodyBuilderApi.assetUrl(body)} download>Tải GLB body</a>
          </div>
        )}
        <div className="vfit-builder-actions">
          <input aria-label="Body ID đã tạo" value={existingBodyId}
            onChange={(event) => setExistingBodyId(event.target.value)}
            placeholder="Dán body ID đã tạo" />
          <button type="button" className="vfit-btn-secondary" disabled={!existingBodyId.trim() || active || creatingBody}
            onClick={() => void useExistingBody()}>Chọn body này</button>
          <button type="button" className="vfit-btn-primary" disabled={active || creatingBody}
            onClick={() => setEditingBody(true)}>Tạo body mới</button>
        </div>
        {creatingBody && <p role="status">Blender đang tạo body MPFB...</p>}
      </section>

      {editingBody && (
        <BodyBuilderStep onBack={() => setEditingBody(false)} disabled={creatingBody}
          onNext={(parameters) => void createBody(parameters)} />
      )}

      {body && (
        <form onSubmit={(event) => void submit(event)}>
          <GarmentImageInputs files={files} onChange={setFiles}
            disabled={active} tryOnImagesOnly />
          <section className="vfit-builder-card" aria-labelledby="tryon-garment-title">
            <h2 id="tryon-garment-title">2. Chuẩn tỉ lệ trang phục</h2>
            <div className="vfit-builder-fields">
              <label>Loại trang phục
                <select value={garmentType} disabled={active}
                  onChange={(event) => setGarmentType(event.target.value as GarmentType)}>
                  <option value="tshirt">Áo thun</option><option value="shirt">Áo sơ mi</option>
                  <option value="jacket">Áo khoác</option><option value="pants">Quần</option>
                  <option value="skirt">Chân váy</option><option value="dress">Váy liền</option>
                </select>
              </label>
              <label>Chiều dài trang phục thật (cm)
                <input type="number" min="1" max="300" step="0.1" required
                  value={garmentLength} disabled={active}
                  onChange={(event) => setGarmentLength(event.target.value)} />
              </label>
            </div>
            <p>Chiều dài thật dùng để đổi tỉ lệ ảnh sang mét. Mặt sau không có ảnh sẽ được suy từ mặt trước.</p>
            <button type="submit" className="vfit-btn-primary"
              disabled={active || !files.front || !garmentLength}>
              {active ? 'Đang xử lý...' : 'Tạo cảnh thử đồ 3D'}
            </button>
          </section>
        </form>
      )}

      {job && !result && job.status !== 'failed' && (
        <section className="vfit-builder-card" role="status">
          <h2>Đang thử đồ</h2>
          <p>Job {job.job_id}: {job.status === 'pending' ? 'đang chờ worker' : 'đang dựng áo và ghép với body'}.</p>
        </section>
      )}
      {error && <p role="alert" className="vfit-builder-error">{error}</p>}
      {result && (
        <section className="vfit-builder-card" aria-labelledby="tryon-result-title">
          <h2 id="tryon-result-title">3. Cảnh thử đồ</h2>
          <p>GLB gồm body MPFB và trang phục dựng từ ảnh. Chưa có điểm fit hoặc khuyến nghị size.</p>
          <Garment360Viewer modelUrl={imageTryOnApi.assetUrl(result.tryon_mesh.url)} />
          <p>Mô phỏng vải: {result.simulation_ran ? 'đã chạy' : 'chưa chạy'}.</p>
          <p>Tỉ lệ điểm xuyên mesh quan sát: {(result.penetration_fraction * 100).toFixed(1)}%.</p>
          {result.warnings.length > 0 && <p>Lưu ý: {result.warnings.join(', ')}</p>}
          <a className="vfit-btn-secondary" href={imageTryOnApi.assetUrl(result.tryon_mesh.url)} download>
            Tải GLB thử đồ
          </a>
        </section>
      )}
    </div>
  );
};
