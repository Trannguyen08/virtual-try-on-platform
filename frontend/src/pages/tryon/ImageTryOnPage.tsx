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
const ESTIMATED_GARMENT_LENGTH_CM: Record<GarmentType, number> = {
  tshirt: 70,
  shirt: 75,
  jacket: 68,
  pants: 100,
  skirt: 60,
  dress: 115,
};

const GARMENT_LABELS: Record<GarmentType, string> = {
  tshirt: 'Áo thun', shirt: 'Áo sơ mi', jacket: 'Áo khoác',
  pants: 'Quần', skirt: 'Chân váy', dress: 'Váy liền',
};

/** Rút gọn UUID — hiện 8 ký tự đầu */
function shortId(id: string) { return id.length > 12 ? `${id.slice(0, 8)}…` : id; }

/** Ánh xạ mã lỗi → thông báo thân thiện */
const ERROR_MESSAGES: Record<string, { title: string; detail: string; hint: string }> = {
  SEVERE_MESH_PENETRATION: {
    title: '⚠️ Không thể căn chỉnh trang phục an toàn',
    detail: 'Mesh cần hiệu chỉnh quá nhiều hoặc vẫn xuyên sâu vào body sau khi căn chỉnh.',
    hint: 'Kiểm tra lại loại trang phục và tải ảnh chụp thẳng, đủ sáng, nền đơn giản để cải thiện mesh.',
  },
  GARMENT_FRAME_INVALID: { title: '⚠️ Trang phục không đúng định dạng', detail: 'File trang phục bị sai hệ trục tọa độ (cần Y-up, mét).', hint: 'Hãy xuất lại file trang phục từ pipeline chuẩn hoặc liên hệ quản trị viên.' },
  BODY_MESH_MISSING: { title: '⚠️ Không tìm thấy body 3D', detail: 'File GLB body không chứa mesh nào hợp lệ.', hint: 'Vui lòng tạo lại body MPFB bằng nút "Tạo body mới" bên trên.' },
  GARMENT_MESH_MISSING: { title: '⚠️ Không tìm thấy mesh trang phục', detail: 'Không dựng được lưới 3D từ ảnh trang phục đã tải lên.', hint: 'Hãy tải ảnh rõ hơn, nền sáng và trang phục chiếm ≥ 60% khung hình.' },
  BODY_SCALE_INVALID: { title: '⚠️ Kích thước body không hợp lệ', detail: 'Chiều cao body GLB nằm ngoài khoảng 1.2–2.3 m.', hint: 'Tạo lại body MPFB với chiều cao người thật của bạn.' },
  BLENDER_TIMEOUT: { title: '⏱ Quá thời gian xử lý', detail: 'Blender mất quá 4 phút để dựng cảnh thử đồ.', hint: 'Thử lại sau vài phút hoặc sử dụng ảnh trang phục nhỏ hơn.' },
  COMPOSITION_FAILED: { title: '❌ Không thể ghép áo và body', detail: 'Quá trình hợp nhất mesh áo và body gặp lỗi không xác định.', hint: 'Thử tải lại ảnh trang phục khác hoặc tạo body mới rồi thử lại.' },
};
function parseFriendlyError(raw: string) {
  for (const [code, msg] of Object.entries(ERROR_MESSAGES)) { if (raw.includes(code)) return msg; }
  return null;
}

/* ── Inline styles ── */
const S = {
  page: { width: '100%', padding: '1.5rem 0 4rem', fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif' } as React.CSSProperties,
  hero: { background: 'linear-gradient(135deg,#14172c 0%,#272b59 55%,#5a46d7 100%)', borderRadius: 24, padding: '2rem 2.5rem', color: '#fff', marginBottom: '2rem', position: 'relative' as const, overflow: 'hidden' } as React.CSSProperties,
  heroPill: { display: 'inline-flex', alignItems: 'center', gap: 6, padding: '5px 12px', border: '1px solid rgba(255,255,255,.22)', borderRadius: 999, background: 'rgba(255,255,255,.1)', fontSize: '.72rem', fontWeight: 800, letterSpacing: '.08em', textTransform: 'uppercase' as const, color: '#d4d8ff', marginBottom: '0.6rem' } as React.CSSProperties,
  heroTitle: { margin: '0 0 0.4rem', fontSize: 'clamp(1.4rem,4vw,2rem)', fontWeight: 800, letterSpacing: '-.04em', lineHeight: 1.1 } as React.CSSProperties,
  heroSub: { margin: 0, color: '#c4c8ee', fontSize: '.9rem', lineHeight: 1.6 } as React.CSSProperties,
  stepRow: { display: 'flex', alignItems: 'center', marginBottom: '1.75rem' } as React.CSSProperties,
  stepCircle: (active: boolean, done: boolean): React.CSSProperties => ({ width: 30, height: 30, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '.78rem', flexShrink: 0, background: done ? '#22c55e' : active ? 'linear-gradient(135deg,#5a46d7,#3b82f6)' : '#e8eaf2', color: done || active ? '#fff' : '#8991aa', boxShadow: active ? '0 4px 10px rgba(90,70,215,.35)' : 'none', transition: 'all .25s' }),
  stepLabel: (active: boolean, done: boolean): React.CSSProperties => ({ fontSize: '.8rem', fontWeight: done || active ? 700 : 500, color: done ? '#16a34a' : active ? '#4a39c7' : '#8991aa', marginLeft: 6 }),
  stepConn: (done: boolean): React.CSSProperties => ({ flex: 1, height: 2, borderRadius: 1, background: done ? '#22c55e' : '#e2e5f0', margin: '0 6px', transition: 'background .3s' }),
  card: { background: '#fff', border: '1px solid #e4e7f0', borderRadius: 20, padding: '1.5rem 1.75rem', marginBottom: '1.25rem', boxShadow: '0 4px 20px rgba(20,23,80,.06)' } as React.CSSProperties,
  cardHead: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' } as React.CSSProperties,
  cardTitle: { fontSize: '.95rem', fontWeight: 700, color: '#172033', margin: 0, display: 'flex', alignItems: 'center', gap: 8 } as React.CSSProperties,
  numBadge: (green?: boolean): React.CSSProperties => ({ width: 24, height: 24, borderRadius: '50%', background: green ? '#dcfce7' : '#eef0ff', color: green ? '#16a34a' : '#4a39c7', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '.72rem', fontWeight: 800, flexShrink: 0 }),
  inputRow: { display: 'flex', gap: 8, marginTop: '0.9rem', flexWrap: 'wrap' as const } as React.CSSProperties,
  btnPrimary: { padding: '0.6rem 1.25rem', borderRadius: 12, border: 'none', background: 'linear-gradient(135deg,#5a46d7,#3b82f6)', color: '#fff', fontWeight: 700, fontSize: '.88rem', cursor: 'pointer', whiteSpace: 'nowrap' as const } as React.CSSProperties,
  btnSecondary: { padding: '0.6rem 1.1rem', borderRadius: 12, border: '1.5px solid #dde1ef', background: '#fff', color: '#4a39c7', fontWeight: 700, fontSize: '.88rem', cursor: 'pointer', whiteSpace: 'nowrap' as const } as React.CSSProperties,
  btnSubmit: { width: '100%', padding: '0.85rem', borderRadius: 14, border: 'none', background: 'linear-gradient(135deg,#14172c,#272b59,#5a46d7)', color: '#fff', fontWeight: 800, fontSize: '1rem', cursor: 'pointer', marginTop: '1.25rem' } as React.CSSProperties,
  fieldGrid: { display: 'grid', gridTemplateColumns: '1fr', gap: '1rem' } as React.CSSProperties,
  fieldLabel: { display: 'flex', flexDirection: 'column' as const, gap: 6, fontSize: '.85rem', fontWeight: 600, color: '#4f586d' } as React.CSSProperties,
  fieldCtrl: { padding: '0.55rem 0.85rem', border: '1.5px solid #dde1ef', borderRadius: 12, fontSize: '.9rem', color: '#172033', background: '#f9fafc', outline: 'none' } as React.CSSProperties,
  statusCard: { background: 'linear-gradient(135deg,#f0f4ff,#e8f4ff)', border: '1.5px solid #c7d9f8', borderRadius: 16, padding: '1rem 1.5rem', display: 'flex', alignItems: 'center', gap: 14, marginBottom: '1rem' } as React.CSSProperties,
  spinner: { width: 26, height: 26, borderRadius: '50%', border: '3px solid #c7d9f8', borderTopColor: '#4a39c7', animation: 'vfit-spin .7s linear infinite', flexShrink: 0 } as React.CSSProperties,
  errBanner: { background: 'linear-gradient(135deg,#fff8f0,#fff1e6)', border: '1.5px solid #f97316', borderRadius: 16, padding: '1.1rem 1.5rem', marginBottom: '1rem', display: 'flex', flexDirection: 'column' as const, gap: '0.45rem' } as React.CSSProperties,
  errHint: { margin: 0, background: '#ffedd5', borderRadius: 10, padding: '0.45rem 0.7rem', fontSize: '.82rem', color: '#7c2d12' } as React.CSSProperties,
  metaChip: { padding: '4px 12px', borderRadius: 999, fontSize: '.78rem', fontWeight: 700, background: '#eef0f5', color: '#4f586d' } as React.CSSProperties,
};

function initialType(product?: Product | null): GarmentType {
  const category = product?.category === 't_shirt' ? 'tshirt' : product?.category;
  return GARMENT_TYPES.find((c) => c === category) ?? 'tshirt';
}

interface Props {
  initialGarment?: Product | null;
  onNavigateCatalog?: () => void;
}

export const ImageTryOnPage: React.FC<Props> = ({ initialGarment }) => {
  const [body, setBody] = useState<BodyBuilderJob | null>(null);
  const [editingBody, setEditingBody] = useState(false);
  const [creatingBody, setCreatingBody] = useState(false);
  const [files, setFiles] = useState<GarmentFiles>({});
  const [garmentType, setGarmentType] = useState<GarmentType>(() => initialType(initialGarment));
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

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!body || !files.front) return;
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setSubmitting(true);
    setError('');
    setJob(null);
    try {
      const created = await imageTryOnApi.create(
        body.body_id || body.job_id,
        { ...files, front: files.front }, garmentType,
        ESTIMATED_GARMENT_LENGTH_CM[garmentType], controller.signal,
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
  const bodyId = body ? (body.body_id || body.job_id) : null;
  const bodyAssetUrl = body ? bodyBuilderApi.assetUrl(body) : '';
  const step1Done = !!body;
  const step2Done = !!result;
  const step2Active = !!body && !result;

  return (
    <>
      <style>{`@keyframes vfit-spin { to { transform: rotate(360deg); } }`}</style>
      <div style={S.page}>

        {/* ── Hero ── */}
        <div style={S.hero}>
          <div style={{ position: 'relative', zIndex: 1 }}>
            <div style={S.heroPill}>✨ AI Try-On 3D</div>
            <h1 style={S.heroTitle}>Thử trang phục từ ảnh</h1>
            <p style={S.heroSub}>Tạo body 3D, tải ảnh trang phục và xem kết quả trực quan ngay lập tức.</p>
          </div>
          <div style={{ position: 'absolute', right: -40, top: -60, width: 200, height: 200, borderRadius: '50%', background: 'rgba(255,255,255,.06)' }} />
        </div>

        {/* ── Step indicator ── */}
        <div style={S.stepRow}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={S.stepCircle(!step1Done, step1Done)}>{step1Done ? '✓' : '1'}</div>
            <span style={S.stepLabel(!step1Done, step1Done)}>Body 3D</span>
          </div>
          <div style={S.stepConn(step1Done)} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={S.stepCircle(step2Active && !step2Done, step2Done)}>{step2Done ? '✓' : '2'}</div>
            <span style={S.stepLabel(step2Active && !step2Done, step2Done)}>Trang phục</span>
          </div>
          <div style={S.stepConn(step2Done)} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={S.stepCircle(!!result, false)}>{result ? '✓' : '3'}</div>
            <span style={S.stepLabel(!!result, false)}>Kết quả</span>
          </div>
        </div>

        {/* ── STEP 1: Body 3D ── */}
        <div style={S.card}>
          <div style={S.cardHead}>
            <h2 style={S.cardTitle}>
              <span style={S.numBadge()}>1</span>
              Body 3D của bạn
            </h2>
          </div>
          {bodyId
            ? <p style={{ margin: '0 0 1rem', color: '#16a34a', fontSize: '.85rem', fontWeight: 600 }}>✅ Body đã sẵn sàng — tiếp tục tải ảnh trang phục bên dưới.</p>
            : <p style={{ margin: '0 0 1rem', color: '#8c94a7', fontSize: '.88rem' }}>Tạo body 3D để xem trước và tiếp tục thử trang phục.</p>
          }
          {bodyId && bodyAssetUrl && (
            <div style={{ marginBottom: '1rem' }}>
              <Garment360Viewer modelUrl={bodyAssetUrl} subject="body" />
            </div>
          )}
          <div style={S.inputRow}>
            <button type="button" style={S.btnPrimary} disabled={active || creatingBody}
              onClick={() => setEditingBody(true)}>{bodyId ? '+ Tạo body mới' : '+ Tạo body'}</button>
            {bodyId && bodyAssetUrl && (
              <a href={bodyAssetUrl} download="body-3d.glb" style={{ ...S.btnSecondary, textDecoration: 'none' }}>
                Tải body GLB
              </a>
            )}
          </div>
          {creatingBody && (
            <div style={{ ...S.statusCard, marginTop: '1rem', marginBottom: 0 }}>
              <div style={S.spinner} />
              <div>
                <div style={{ fontWeight: 700, fontSize: '.88rem' }}>Đang tạo body…</div>
                <div style={{ color: '#677089', fontSize: '.8rem' }}>Blender đang dựng mô hình 3D</div>
              </div>
            </div>
          )}
        </div>

        {/* ── Body builder form ── */}
        {editingBody && (
          <div style={{ ...S.card, border: '1.5px solid #c7cef8' }}>
            <BodyBuilderStep onBack={() => setEditingBody(false)} disabled={creatingBody}
              onNext={(p) => void createBody(p)} />
          </div>
        )}

        {/* ── STEP 2: Garment ── */}
        {body && (
          <form onSubmit={(e) => void submit(e)}>
            <div style={{ marginBottom: '1.25rem' }}>
              <GarmentImageInputs files={files} onChange={setFiles} disabled={active} tryOnImagesOnly />
            </div>
            <div style={S.card}>
              <div style={S.cardHead}>
                <h2 style={S.cardTitle}>
                  <span style={S.numBadge()}>2</span>
                  Thông tin trang phục
                </h2>
              </div>
              <div style={S.fieldGrid}>
                <label style={S.fieldLabel}>
                  Loại trang phục
                  <select value={garmentType} disabled={active}
                    onChange={(e) => setGarmentType(e.target.value as GarmentType)}
                    style={S.fieldCtrl}>
                    {GARMENT_TYPES.map((t) => <option key={t} value={t}>{GARMENT_LABELS[t]}</option>)}
                  </select>
                </label>
              </div>
              <p style={{ margin: '0.6rem 0 0', color: '#8c94a7', fontSize: '.8rem' }}>
                💡 Tỉ lệ được ước lượng theo loại trang phục; mặt sau không có ảnh sẽ được suy từ mặt trước.
              </p>
              <button type="submit"
                style={{ ...S.btnSubmit, opacity: active || !files.front ? .5 : 1, cursor: active || !files.front ? 'not-allowed' : 'pointer' }}
                disabled={active || !files.front}>
                {active ? '⏳ Đang xử lý…' : '✨ Tạo cảnh thử đồ 3D'}
              </button>
            </div>
          </form>
        )}

        {/* ── Processing ── */}
        {job && !result && job.status !== 'failed' && (
          <div style={S.statusCard} role="status">
            <div style={S.spinner} />
            <div>
              <div style={{ fontWeight: 700, fontSize: '.9rem' }}>
                {job.status === 'pending' ? 'Đang xếp hàng chờ…' : 'Đang tái dựng trang phục và ghép cảnh 3D…'}
              </div>
              <div style={{ color: '#677089', fontSize: '.8rem', marginTop: 2 }}>
                Job <code style={{ fontFamily: 'monospace', background: '#eef0ff', padding: '1px 5px', borderRadius: 4, color: '#4a39c7' }}>{shortId(job.job_id)}</code>{' '}— thường mất 1–3 phút
              </div>
            </div>
          </div>
        )}

        {/* ── Error ── */}
        {error && (() => {
          const friendly = parseFriendlyError(error);
          return friendly ? (
            <div style={S.errBanner} role="alert">
              <strong style={{ fontSize: '.92rem', color: '#c2410c' }}>{friendly.title}</strong>
              <p style={{ margin: 0, color: '#431407', fontSize: '.86rem' }}>{friendly.detail}</p>
              <p style={S.errHint}>💡 <strong>Gợi ý:</strong> {friendly.hint}</p>
              <div style={{ display: 'flex', gap: 8, marginTop: 4, flexWrap: 'wrap' }}>
                <button type="button" style={S.btnPrimary} onClick={() => { setError(''); setJob(null); }}>Thử lại</button>
                <button type="button" style={S.btnSecondary} onClick={() => { setError(''); setJob(null); setEditingBody(true); }}>Tạo body mới</button>
              </div>
            </div>
          ) : <p role="alert" className="vfit-builder-error">{error}</p>;
        })()}

        {/* ── STEP 3: Result ── */}
        {result && (
          <div style={S.card}>
            <div style={S.cardHead}>
              <h2 style={S.cardTitle}>
                <span style={S.numBadge(true)}>✓</span>
                Cảnh thử đồ 3D
              </h2>
              <a style={{ ...S.btnSecondary, textDecoration: 'none', fontSize: '.82rem', padding: '5px 14px' }}
                href={imageTryOnApi.assetUrl(result.tryon_mesh.url)} download>↓ Tải GLB</a>
            </div>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: '1rem' }}>
              <span style={S.metaChip}>Xuyên mesh: {(result.penetration_fraction * 100).toFixed(1)}%</span>
              <span style={{ ...S.metaChip, background: result.simulation_ran ? '#dcfce7' : '#f0f4ff', color: result.simulation_ran ? '#166534' : '#4a39c7' }}>
                {result.simulation_ran ? '✅ Mô phỏng vải đã chạy' : 'Mô phỏng vải: chưa chạy'}
              </span>
              {result.warnings.length > 0 && (
                <span style={{ ...S.metaChip, background: '#fef9c3', color: '#854d0e' }}>⚠️ {result.warnings.join(', ')}</span>
              )}
            </div>
            <Garment360Viewer modelUrl={imageTryOnApi.assetUrl(result.tryon_mesh.url)} />
          </div>
        )}

      </div>
    </>
  );
};
