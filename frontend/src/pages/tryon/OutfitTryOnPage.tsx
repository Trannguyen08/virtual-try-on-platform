import React, { useEffect, useRef, useState } from 'react';
import { bodyBuilderApi, BodyBuilderJob, BodyParameters } from '../../api/bodyBuilderApi';
import { GarmentType } from '../../api/garment3d';
import { imageTryOnApi } from '../../api/imageTryOnApi';
import { GarmentFiles, GarmentImageInputs } from '../../components/GarmentImageInputs';
import { BodyBuilderStep } from '../../components/tryon/BodyBuilderStep';
import { BodyPhotoCapture } from '../../components/tryon/BodyPhotoCapture';
import { OutfitLayer, OutfitViewer } from '../../components/tryon/OutfitViewer';
import { Product } from '../../data/mockProducts';
import { useGarmentProducts } from '../../hooks/useGarmentProducts';
import '../../styles/outfit.css';

type Slot = 'top' | 'bottom' | 'dress';
interface Choice {
  key: string;
  product?: Product;
  files: GarmentFiles;
  type: GarmentType;
  length: number;
  size: string;
}
interface Applied { key: string; layer: OutfitLayer; note: string }
interface Pending { key: string; jobId: string; bodyId: string }
type Choices = Partial<Record<Slot, Choice>>;
type Results = Partial<Record<Slot, Applied>>;
const SLOTS: Slot[] = ['top', 'bottom', 'dress'];
const LABELS: Record<Slot, string> = { top: 'Áo', bottom: 'Quần / chân váy', dress: 'Váy liền' };
const TYPES: Record<Slot, { value: GarmentType; label: string; length: number }[]> = {
  top: [{ value: 'tshirt', label: 'Áo thun', length: 70 }, { value: 'shirt', label: 'Áo sơ mi', length: 75 }, { value: 'jacket', label: 'Áo khoác', length: 68 }],
  bottom: [{ value: 'pants', label: 'Quần', length: 100 }, { value: 'skirt', label: 'Chân váy', length: 60 }],
  dress: [{ value: 'dress', label: 'Váy liền', length: 115 }],
};
const BODY_KEY = 'tryon.mpfb.body_id';
const OUTFIT_KEY = 'tryon.outfit.v1';
const slotOf = (product: Product): Slot => product.category === 'pants' ? 'bottom' : product.category === 'dress' ? 'dress' : 'top';
const newUpload = (slot: Slot): Choice => ({ key: crypto.randomUUID(), files: {}, type: TYPES[slot][0].value, length: TYPES[slot][0].length, size: 'M' });
const fromProduct = (product: Product, size?: string): Choice => {
  const type = product.category === 't_shirt' ? 'tshirt' : product.category;
  return { key: crypto.randomUUID(), product, files: {}, type,
    length: TYPES[slotOf(product)].find((item) => item.value === type)?.length || 70,
    size: size && product.sizes.includes(size as Product['sizes'][number]) ? size : product.sizes.includes('M') ? 'M' : product.sizes[0] || 'M' };
};

function readSaved(): { bodyId?: string; choices?: Choices; results?: Results; pending?: Partial<Record<Slot, Pending>> } {
  try {
    const value = JSON.parse(window.sessionStorage.getItem(OUTFIT_KEY) || '{}');
    return value && typeof value === 'object' ? value : {};
  } catch { return {}; }
}

export function OutfitTryOnPage({ initialGarment, initialSize, onNavigateCatalog }: {
  initialGarment?: Product | null;
  initialSize?: string;
  onNavigateCatalog?: () => void;
}) {
  const { products, refitStatus, catalogLoaded } = useGarmentProducts();
  const [body, setBody] = useState<BodyBuilderJob | null>(null);
  const [restoring, setRestoring] = useState(true);
  const [editingBody, setEditingBody] = useState(false);
  const [creating, setCreating] = useState(false);
  const [choices, setChoices] = useState<Choices>(() => readSaved().choices || {});
  const [results, setResults] = useState<Results>({});
  const [imageJobs, setImageJobs] = useState<Partial<Record<Slot, Pending>>>(() => readSaved().pending || {});
  const [tab, setTab] = useState<Slot>(initialGarment ? slotOf(initialGarment) : 'top');
  const [source, setSource] = useState<'catalog' | 'upload'>('catalog');
  const [search, setSearch] = useState('');
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const controllerRef = useRef<AbortController | null>(null);
  const lock = useRef(false);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    let savedId: string | null = null;
    try { savedId = window.localStorage.getItem(BODY_KEY); } catch { /* Browser storage can be disabled. */ }
    if (savedId) {
      void bodyBuilderApi.getBody(savedId).then((restored) => {
        if (!mounted.current) return;
        setBody(restored);
        const saved = readSaved();
        if (saved.bodyId === savedId) setResults(saved.results || {});
      }).catch(() => {
        if (mounted.current) setError('Không tải được model đã lưu. Kiểm tra backend hoặc tạo model mới.');
      }).finally(() => { if (mounted.current) setRestoring(false); });
    } else setRestoring(false);
    return () => { mounted.current = false; controllerRef.current?.abort(); };
  }, []);

  // Re-entering from a product page replaces only its slot, preserving the other piece.
  useEffect(() => {
    if (!initialGarment) return;
    const slot = slotOf(initialGarment);
    setChoices((previous) => {
      const existing = previous[slot];
      const choice = existing?.product?.id === initialGarment.id && (!initialSize || existing.size === initialSize)
        ? existing : fromProduct(initialGarment, initialSize);
      return { ...(slot === 'dress' ? {} : { top: previous.top, bottom: previous.bottom }), [slot]: choice };
    });
    setTab(slot); setSource('catalog');
  }, [initialGarment, initialSize]);

  useEffect(() => {
    if (!catalogLoaded || restoring) return;
    const allowed = new Set(products.map((product) => product.id));
    const removed = SLOTS.filter((slot) => choices[slot]?.product && !allowed.has(choices[slot]!.product!.id));
    if (!removed.length) return;
    setChoices((previous) => { const next = { ...previous }; removed.forEach((slot) => delete next[slot]); return next; });
    setResults((previous) => { const next = { ...previous }; removed.forEach((slot) => delete next[slot]); return next; });
    setImageJobs((previous) => { const next = { ...previous }; removed.forEach((slot) => delete next[slot]); return next; });
    setNotice('Sản phẩm cũ đã được gỡ khỏi thư viện. Chọn mẫu mới để tiếp tục phối đồ.');
  }, [catalogLoaded, products, restoring, choices]);

  useEffect(() => {
    if (restoring) return;
    // Store product choices and completed asset URLs only; never persist personal photos/files.
    const savedChoices: Choices = {};
    SLOTS.forEach((slot) => { if (choices[slot]) savedChoices[slot] = { ...choices[slot]!, files: {} }; });
    try {
      window.sessionStorage.setItem(OUTFIT_KEY, JSON.stringify({ bodyId: body?.body_id || body?.job_id, choices: savedChoices, results, pending: imageJobs }));
    } catch { /* The live fitting room still works when browser storage is unavailable. */ }
  }, [choices, results, body, restoring, imageJobs]);

  const choose = (slot: Slot, choice: Choice) => {
    setChoices((previous) => ({ ...(slot === 'dress' ? {} : { top: previous.top, bottom: previous.bottom }), [slot]: choice }));
    setResults((previous) => slot === 'dress' ? { dress: previous.dress } : { top: previous.top, bottom: previous.bottom });
    setNotice(slot === 'dress' ? 'Váy liền thay cho cả áo và quần.' : 'Đổi riêng món này; món còn lại được giữ nguyên.');
    setError('');
  };
  const update = (patch: Partial<Choice>) => {
    const choice = choices[tab] || newUpload(tab);
    choose(tab, { ...choice, ...patch, key: crypto.randomUUID() });
  };
  const remove = (slot: Slot) => {
    setChoices((previous) => { const next = { ...previous }; delete next[slot]; return next; });
    setResults((previous) => { const next = { ...previous }; delete next[slot]; return next; });
    setImageJobs((previous) => { const next = { ...previous }; delete next[slot]; return next; });
  };

  const createBody = async (parameters: BodyParameters) => {
    if (lock.current) return;
    lock.current = true; setCreating(true); setError('');
    const controller = new AbortController(); controllerRef.current = controller;
    try {
      const created = await bodyBuilderApi.generate(parameters, controller.signal);
      if (!mounted.current) return;
      setBody(created); setResults({}); setImageJobs({}); setEditingBody(false);
      try { window.localStorage.setItem(BODY_KEY, created.body_id || created.job_id); } catch { /* Keep the new body usable in memory. */ }
      setNotice('Model đã sẵn sàng. Chọn áo và quần để phối bộ đồ đầu tiên.');
    } catch (reason) {
      if (mounted.current) setError(reason instanceof Error ? reason.message : 'Không tạo được model.');
    } finally {
      lock.current = false;
      if (mounted.current) setCreating(false);
    }
  };

  const apply = async () => {
    if (!body || lock.current) return;
    lock.current = true; setBusy(true); setError('');
    const controller = new AbortController(); controllerRef.current = controller;
    try {
      for (const slot of SLOTS) {
        const choice = choices[slot];
        if (!choice || choice.key === results[slot]?.key) continue;
        const label = choice.product?.name || `${LABELS[slot]} từ ảnh của bạn`;
        setStatus(`Đang chuẩn bị ${label}…`);
        let applied: Applied;
        if (choice.product?.fittingMode) {
          const clothing = await bodyBuilderApi.clothing(body.job_id, choice.product.id,
            choice.product.category, choice.product.colors[0]?.hex || '#ffffff', choice.size, controller.signal);
          if (controller.signal.aborted) return;
          applied = { key: choice.key, layer: { url: bodyBuilderApi.assetUrl(clothing), label, kind: 'catalog' },
            note: choice.product.fittingMode === 'body_refit' ? 'Refit theo model; chưa kiểm chứng size thực tế.' : 'Căn theo chiều cao; giữ tư thế gốc của trang phục.' };
        } else {
          const pendingJob = imageJobs[slot];
          const bodyId = body.body_id || body.job_id;
          const canResume = pendingJob?.key === choice.key && pendingJob.bodyId === bodyId;
          let front = choice.files.front;
          if (!canResume && !front && choice.product) {
            try {
              const response = await fetch(choice.product.imageUrl, { signal: controller.signal });
              if (!response.ok) throw new Error('Image unavailable');
              const blob = await response.blob();
              if (!['image/jpeg', 'image/png', 'image/webp'].includes(blob.type)) throw new Error('Unsupported image');
              front = new File([blob], 'product-front.image', { type: blob.type });
            } catch (reason) {
              if (controller.signal.aborted) throw reason;
              throw new Error(`Không tải được ảnh ${label}. Chọn “Ảnh sản phẩm ngoài” và tải ảnh mặt trước từ thiết bị.`);
            }
          }
          if (!canResume && !front) throw new Error(`Hãy tải ảnh mặt trước cho ${LABELS[slot].toLowerCase()}.`);
          let job = canResume
            ? await imageTryOnApi.get(pendingJob.jobId, controller.signal)
            : await imageTryOnApi.create(bodyId,
              { ...choice.files, front: front! }, choice.type, choice.length, controller.signal);
          if (!mounted.current || controller.signal.aborted) return;
          setImageJobs((previous) => ({ ...previous, [slot]: { key: choice.key, jobId: job.job_id, bodyId } }));
          const deadline = Date.now() + 20 * 60 * 1000;
          while (job.status === 'pending' || job.status === 'running') {
            if (Date.now() > deadline) throw new Error(`Hết thời gian chờ ${label}. Kiểm tra worker rồi thử lại.`);
            setStatus(`${LABELS[slot]} đang ${job.status === 'pending' ? 'chờ worker' : 'được dựng và căn theo model'}…`);
            await new Promise((resolve) => window.setTimeout(resolve, 2500));
            controller.signal.throwIfAborted();
            job = await imageTryOnApi.get(job.job_id, controller.signal);
          }
          if (job.status !== 'completed' || !job.result) {
            setImageJobs((previous) => { const next = { ...previous }; delete next[slot]; return next; });
            throw new Error(`${label}: ${job.error?.message || 'Không thể xử lý trang phục.'}`);
          }
          applied = { key: choice.key, layer: { url: imageTryOnApi.assetUrl(job.result.tryon_mesh.url), label, kind: 'image' },
            note: `${job.result.source === 'mock' ? 'Kết quả minh họa. ' : ''}${job.result.simulation_ran ? 'Đã mô phỏng riêng món này.' : 'Xem trước tĩnh, chưa mô phỏng vải.'}${job.result.warnings.length ? ` ${job.result.warnings.join(', ')}` : ''}` };
          setImageJobs((previous) => { const next = { ...previous }; delete next[slot]; return next; });
        }
        if (!mounted.current || controller.signal.aborted) return;
        setResults((previous) => ({ ...previous, [slot]: applied }));
      }
      setNotice('Đã cập nhật bộ đồ. Bạn có thể đổi riêng áo hoặc quần và tiếp tục phối.');
    } catch (reason) {
      if (mounted.current && !controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Không thể cập nhật bộ đồ.');
    } finally {
      lock.current = false;
      if (mounted.current) { setBusy(false); setStatus(''); }
    }
  };

  const current = choices[tab];
  const disabled = busy || creating || restoring;
  const selectedSlots = SLOTS.filter((slot) => choices[slot]);
  const pending = selectedSlots.filter((slot) => choices[slot]?.key !== results[slot]?.key);
  const canResumeSlot = (slot: Slot) => imageJobs[slot]?.key === choices[slot]?.key && imageJobs[slot]?.bodyId === (body?.body_id || body?.job_id);
  const invalid = pending.some((slot) => !choices[slot]?.product && !choices[slot]?.files.front && !canResumeSlot(slot));
  const visibleResults = SLOTS.filter((slot) => results[slot] && (choices.dress ? slot === 'dress' : slot !== 'dress'));
  const visibleProducts = products.filter((product) => slotOf(product) === tab && product.name.toLocaleLowerCase('vi').includes(search.toLocaleLowerCase('vi')));

  return <div className="outfit-page">
    <header className="outfit-hero">
      <div><span className="outfit-eyebrow">PHÒNG THỬ ĐỒ CỦA BẠN</span><h1>Một model. Nhiều cách phối.</h1>
        <p>Chọn áo, đổi quần, tìm bộ đồ hợp với bạn — từ bộ sưu tập hoặc ảnh sản phẩm bên ngoài.</p></div>
      <button type="button" onClick={onNavigateCatalog}>Khám phá sản phẩm ↗</button>
    </header>
    <ol className="outfit-steps" aria-label="Các bước thử đồ">
      <li className={!body ? 'active' : ''}><b>{body ? '✓' : '1'}</b> Model của bạn</li>
      <li className={body && !visibleResults.length ? 'active' : ''}><b>2</b> Phối áo & quần</li>
      <li className={visibleResults.length ? 'active' : ''}><b>3</b> Xem & đổi từng món</li>
    </ol>
    {restoring && <p role="status">Đang mở phòng thử đồ…</p>}
    {!restoring && <section className="outfit-body-setup" hidden={!!body && !editingBody}>
      <BodyPhotoCapture active={!body || editingBody} />
      <div className="outfit-panel"><BodyBuilderStep disabled={creating} onBack={() => body ? setEditingBody(false) : onNavigateCatalog?.()} onNext={(parameters) => void createBody(parameters)} /></div>
    </section>}
    {creating && <p className="outfit-progress" role="status">Đang tạo model 3D bằng Blender. Bạn có thể giữ nguyên trang này…</p>}
    {error && <p className="outfit-error" role="alert">{error}</p>}
    {body && !editingBody && <div className="outfit-workspace">
      <section className="outfit-stage outfit-panel">
        <div className="outfit-section-heading"><div><span className="outfit-eyebrow">GƯƠNG THỬ ĐỒ 3D</span><h2>Bộ đồ của bạn</h2></div>
          <button type="button" disabled={disabled} onClick={() => setEditingBody(true)}>Đổi model</button></div>
        <OutfitViewer bodyUrl={bodyBuilderApi.assetUrl(body)} layers={visibleResults.map((slot) => results[slot]!.layer)} />
        <div className="outfit-wearing" aria-label="Trang phục đang hiển thị">
          {!visibleResults.length && <p>Model đã sẵn sàng. Chọn một chiếc áo và một chiếc quần để bắt đầu.</p>}
          {visibleResults.map((slot) => <div key={slot}><strong>{LABELS[slot]}</strong><span>{results[slot]!.layer.label}</span><small>{results[slot]!.note} <a href={results[slot]!.layer.url} download>Tải cảnh riêng món này</a></small></div>)}
        </div>
        <p className="outfit-note">Xem trước phối đồ trên cùng model. Chưa đánh giá độ vừa theo size hoặc mô phỏng tương tác vải giữa áo và quần. <a href={bodyBuilderApi.assetUrl(body)} download>Tải model cơ thể</a></p>
      </section>
      <section className="outfit-wardrobe outfit-panel">
        <span className="outfit-eyebrow">TỦ ĐỒ MỞ</span><h2>Hôm nay bạn mặc gì?</h2>
        <p className="outfit-note">Đổi áo vẫn giữ quần. Đổi quần vẫn giữ áo.</p>
        <div className="outfit-tabs" role="group" aria-label="Chọn phần trang phục">
          {SLOTS.map((slot) => <button type="button" key={slot} aria-pressed={tab === slot} className={tab === slot ? 'active' : ''}
            disabled={disabled} onClick={() => { setTab(slot); setSearch(''); }}>{LABELS[slot]}{choices[slot] ? ' •' : ''}</button>)}
        </div>
        {tab === 'dress' && <p className="outfit-note">Váy liền thay cho cả áo và quần trong bộ đồ.</p>}
        <div className="outfit-source" role="group" aria-label="Nguồn sản phẩm">
          <button type="button" disabled={disabled} aria-pressed={source === 'catalog'} className={source === 'catalog' ? 'active' : ''} onClick={() => setSource('catalog')}>Trong bộ sưu tập</button>
          <button type="button" disabled={disabled} aria-pressed={source === 'upload'} className={source === 'upload' ? 'active' : ''} onClick={() => setSource('upload')}>Ảnh sản phẩm ngoài</button>
        </div>
        {source === 'catalog' ? <>
          <label className="outfit-search"><span className="outfit-sr-only">Tìm sản phẩm</span><input type="search" placeholder={`Tìm ${LABELS[tab].toLowerCase()}…`} value={search} onChange={(event) => setSearch(event.target.value)} /></label>
          <p className="outfit-note">{refitStatus}</p>
          <div className="outfit-product-grid">
            {visibleProducts.map((product) => <button key={product.id} type="button" disabled={disabled} className={`outfit-product ${current?.product?.id === product.id ? 'selected' : ''}`}
              aria-pressed={current?.product?.id === product.id} onClick={() => choose(tab, fromProduct(product))}>
              <div><img src={product.imageUrl} alt="" loading="lazy" /><span>{product.fittingMode ? 'Asset 3D' : 'Dựng từ ảnh'}</span></div>
              <strong>{product.name}</strong><small>{product.price ? `${product.price.toLocaleString('vi-VN')}₫` : 'Có trong kho trang phục'}</small>
            </button>)}
          </div>
          {!visibleProducts.length && <p className="outfit-empty">Chưa có sản phẩm phù hợp. Thử từ khóa khác hoặc tải ảnh sản phẩm của bạn.</p>}
        </> : <div className="outfit-external">
          <p>Thấy món đồ ở cửa hàng khác? Lưu ảnh sản phẩm rồi tải vào đây. Dùng ảnh riêng từng món, mặt trước rõ và nền đơn giản.</p>
          {current?.product ? <button type="button" disabled={disabled} onClick={() => choose(tab, newUpload(tab))}>+ Thêm {LABELS[tab].toLowerCase()} từ ảnh mới</button>
            : <>
              <GarmentImageInputs key={tab} files={current?.files || {}} onChange={(files) => update({ files })} disabled={disabled} tryOnImagesOnly />
              <div className="outfit-fields">
                <label>Loại trang phục<select disabled={disabled} value={current?.type || TYPES[tab][0].value} onChange={(event) => {
                  const option = TYPES[tab].find((item) => item.value === event.target.value)!;
                  update({ type: option.value, length: option.length });
                }}>{TYPES[tab].map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>
                <label>Chiều dài sản phẩm (cm)<input type="number" min={10} max={250} step="0.5" disabled={disabled} value={current?.length ?? TYPES[tab][0].length}
                  onChange={(event) => { const length = Number(event.target.value); if (Number.isFinite(length)) update({ length }); }} /></label>
              </div>
              <p className="outfit-note">Chiều dài đang là giá trị tham khảo; nhập chiều dài thật để căn tỉ lệ. Thiếu ảnh mặt sau sẽ được ước lượng.</p>
            </>}
        </div>}
        {current?.product?.fittingMode && <label className="outfit-size">Nhãn size (chưa kiểm chứng độ vừa)<select disabled={disabled} value={current.size} onChange={(event) => update({ size: event.target.value })}>
          {current.product.sizes.map((size) => <option key={size}>{size}</option>)}</select></label>}
        <div className="outfit-selection">
          <h3>Bộ đồ đã chọn <span>{selectedSlots.length} món</span></h3>
          {!selectedSlots.length && <p>Chọn áo và quần riêng để phối cùng nhau.</p>}
          {selectedSlots.map((slot) => <div className="outfit-selected-row" key={slot}>
            <div><strong>{LABELS[slot]} · {choices[slot]?.product?.name || 'Ảnh của bạn'}</strong><small>{choices[slot]?.key === results[slot]?.key ? 'Đang mặc trên model' : 'Chưa áp dụng'}</small></div>
            <button type="button" disabled={disabled} aria-label={`Bỏ ${LABELS[slot].toLowerCase()}`} onClick={() => remove(slot)}>Bỏ</button>
          </div>)}
          <button type="button" className="outfit-primary outfit-apply" disabled={disabled || !pending.length || invalid || selectedSlots.some((slot) => choices[slot]!.length < 10 || choices[slot]!.length > 250)} onClick={() => void apply()}>
            {busy ? 'Đang cập nhật bộ đồ…' : pending.some(canResumeSlot) ? 'Tiếp tục xử lý bộ đồ' : pending.length ? `Thử ${pending.length} món đã chọn` : visibleResults.length ? 'Bộ đồ đã được cập nhật' : 'Chọn trang phục để bắt đầu'}
          </button>
          {status && <p role="status" className="outfit-progress">{status}</p>}
          {!busy && pending.some(canResumeSlot) && <p className="outfit-note">Job đã gửi vẫn có thể chạy trên server. Bấm tiếp tục để theo dõi, hoặc bỏ món và chọn lại nếu muốn tạo yêu cầu mới.</p>}
          {invalid && <p className="outfit-note">Ảnh tải lên chưa được lưu khi rời trang. Chọn lại mặt trước của món chưa áp dụng để tiếp tục.</p>}
          {notice && !busy && <p role="status" className="outfit-note">{notice}</p>}
        </div>
      </section>
    </div>}
  </div>;
}
