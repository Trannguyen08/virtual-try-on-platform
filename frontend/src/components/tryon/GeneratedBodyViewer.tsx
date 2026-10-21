import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { bodyBuilderApi, BodyBuilderJob } from '../../api/bodyBuilderApi';
import { Product } from '../../data/mockProducts';

interface Props {
  bodyJob: BodyBuilderJob;
  initialClothingJob: BodyBuilderJob | null;
  initialError?: string;
  garment: Product;
  selectedSize: string;
  onRestart: () => void;
  onTryAnotherSize: () => void;
}

export const GeneratedBodyViewer: React.FC<Props> = ({
  bodyJob, initialClothingJob, initialError = '', garment, selectedSize, onRestart, onTryAnotherSize,
}) => {
  const mount = useRef<HTMLDivElement>(null);
  const controls = useRef<OrbitControls | null>(null);
  const model = useRef<THREE.Group | null>(null);
  const [clothingJob, setClothingJob] = useState(initialClothingJob);
  const [layer, setLayer] = useState<'body' | 'clothed'>(initialClothingJob ? 'clothed' : 'body');
  const [wireframe, setWireframe] = useState(false);
  const wireframeRef = useRef(false);
  wireframeRef.current = wireframe;
  const [autoRotate, setAutoRotate] = useState(false);
  const [color, setColor] = useState(garment.colors[0]?.hex || '#ffffff');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(initialError);
  const [loadError, setLoadError] = useState('');
  const currentJob = layer === 'body' || !clothingJob ? bodyJob : clothingJob;
  const isMpfbRefit = clothingJob?.method === 'blender_mpfb_refit';
  const url = bodyBuilderApi.assetUrl(currentJob);

  useEffect(() => {
    const container = mount.current;
    if (!container || !url) return;
    let cancelled = false;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 100);
    camera.position.set(0, 1, 3.2);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    container.appendChild(renderer.domElement);
    scene.add(new THREE.HemisphereLight(0xffffff, 0xc6c9d8, 2.2));
    const key = new THREE.DirectionalLight(0xffffff, 2);
    key.position.set(2, 4, 3);
    scene.add(key);
    const orbit = new OrbitControls(camera, renderer.domElement);
    controls.current = orbit;
    orbit.enableDamping = true;
    orbit.minDistance = 0.5;
    orbit.maxDistance = 8;
    orbit.maxPolarAngle = Math.PI * 0.85;
    orbit.autoRotate = autoRotate;
    const resize = () => {
      const width = container.clientWidth || 600;
      const height = container.clientHeight || 600;
      renderer.setSize(width, height);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };
    const observer = new ResizeObserver(resize);
    observer.observe(container);
    resize();
    new GLTFLoader().load(url, (gltf) => {
      if (cancelled) {
        gltf.scene.traverse((node) => {
          if (node instanceof THREE.Mesh) {
            node.geometry.dispose();
            const materials = Array.isArray(node.material) ? node.material : [node.material];
            materials.forEach((material) => material.dispose());
          }
        });
        return;
      }
      const object = gltf.scene;
      model.current = object;
      object.traverse((node) => {
        if (node instanceof THREE.Mesh) {
          const materials = Array.isArray(node.material) ? node.material : [node.material];
          materials.forEach((material) => { (material as THREE.MeshStandardMaterial).wireframe = wireframeRef.current; });
        }
      });
      const bounds = new THREE.Box3().setFromObject(object);
      const center = bounds.getCenter(new THREE.Vector3());
      const size = bounds.getSize(new THREE.Vector3());
      object.position.x -= center.x;
      object.position.z -= center.z;
      object.position.y -= bounds.min.y;
      orbit.target.set(0, size.y * 0.5, 0);
      camera.position.set(0, size.y * 0.5, Math.max(2.4, size.y * 1.5));
      orbit.update();
      scene.add(object);
      setLoadError('');
    }, undefined, () => { if (!cancelled) setLoadError('Không tải được mẫu 3D. Vui lòng tạo lại mô hình.'); });
    let frame = 0;
    const animate = () => {
      frame = requestAnimationFrame(animate);
      orbit.update();
      renderer.render(scene, camera);
    };
    animate();
    return () => {
      cancelled = true;
      cancelAnimationFrame(frame);
      observer.disconnect();
      orbit.dispose();
      controls.current = null;
      model.current = null;
      scene.traverse((node) => {
        if (node instanceof THREE.Mesh) {
          node.geometry.dispose();
          const materials = Array.isArray(node.material) ? node.material : [node.material];
          materials.forEach((material) => material.dispose());
        }
      });
      renderer.dispose();
      container.removeChild(renderer.domElement);
    };
  }, [url]);

  useEffect(() => { if (controls.current) controls.current.autoRotate = autoRotate; }, [autoRotate]);
  useEffect(() => {
    model.current?.traverse((node) => {
      if (node instanceof THREE.Mesh) {
        const materials = Array.isArray(node.material) ? node.material : [node.material];
        materials.forEach((material) => { (material as THREE.MeshStandardMaterial).wireframe = wireframe; });
      }
    });
  }, [wireframe]);

  const applyColor = async (nextColor: string) => {
    setBusy(true);
    setError('');
    try {
      const job = await bodyBuilderApi.clothing(bodyJob.job_id, garment.id, garment.category, nextColor, selectedSize);
      setColor(nextColor);
      setClothingJob(job);
      setLayer('clothed');
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Không thể cập nhật trang phục');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="vfit-builder-result">
      <div className="vfit-builder-result-header">
        <button className="vfit-btn-secondary" type="button" onClick={onRestart}>Tạo mẫu cơ thể khác</button>
        <div><h2>Mẫu cơ thể 3D</h2><span>Mô hình thử đồ</span></div>
      </div>
      <div className="vfit-builder-layout">
        <section className="vfit-builder-viewport">
          <div className="vfit-3d-layer-pills">
            <button type="button" aria-pressed={layer === 'body'} className={`vfit-layer-btn ${layer === 'body' ? 'active' : ''}`} onClick={() => setLayer('body')}>Cơ thể</button>
            <button type="button" disabled={!clothingJob} aria-pressed={layer === 'clothed'} className={`vfit-layer-btn ${layer === 'clothed' ? 'active' : ''}`} onClick={() => setLayer('clothed')}>Có trang phục</button>
          </div>
          <div ref={mount} className="vfit-builder-canvas" />
          {loadError && <div className="vfit-builder-error">{loadError}</div>}
          <div className="vfit-3d-floating-toolbar">
            <button type="button" className="vfit-layer-btn" onClick={() => { if (controls.current) controls.current.object.position.multiplyScalar(0.85); }}>＋</button>
            <button type="button" className="vfit-layer-btn" onClick={() => { if (controls.current) controls.current.object.position.multiplyScalar(1.15); }}>－</button>
            <button type="button" className="vfit-layer-btn" onClick={() => {
              if (controls.current) {
                controls.current.object.position.set(0, controls.current.target.y, 3.2);
                controls.current.update();
              }
            }}>Góc đầu</button>
            <button type="button" aria-pressed={autoRotate} className={`vfit-layer-btn ${autoRotate ? 'active' : ''}`} onClick={() => setAutoRotate(!autoRotate)}>Tự xoay</button>
            <button type="button" aria-pressed={wireframe} className={`vfit-layer-btn ${wireframe ? 'active' : ''}`} onClick={() => setWireframe(!wireframe)}>Khung lưới</button>
            <a className="vfit-layer-btn" href={url} download={`body-${currentJob.job_id}.glb`}>Tải GLB</a>
          </div>
        </section>
        <section className="vfit-builder-card">
          <span className="vfit-builder-eyebrow">Mô hình thử đồ</span>
          <h3>{garment.name}</h3>
          <p>Size đã chọn: <strong>{selectedSize}</strong></p>
          <p>Mẫu cơ thể được tạo từ thông số đã chọn. {isMpfbRefit ? 'Trang phục được căn theo mẫu cơ thể và giữ chất liệu gốc.' : clothingJob?.method === 'blender_asset_clothing' ? 'Trang phục dùng mô hình 3D đã cung cấp.' : clothingJob ? 'Trang phục là bản xem trước theo loại sản phẩm.' : 'Chưa tạo được trang phục.'} Ảnh tải lên chưa được dùng để dựng mẫu cơ thể. Bản xem trước này chưa mô phỏng chuyển động vải hoặc xác nhận độ vừa vặn.</p>
          {isMpfbRefit && <p>Áo và quần được căn theo dáng mẫu; kết quả chưa thay thế việc kiểm tra size thực tế.</p>}
          <div className="vfit-builder-presets">
            <span>Màu trang phục</span>
            {garment.colors.map((item) => (
              <button key={item.hex} type="button" title={item.name} aria-label={item.name}
                aria-pressed={color === item.hex}
                className={`vfit-builder-swatch ${color === item.hex ? 'active' : ''}`}
                style={{ backgroundColor: item.hex }} disabled={busy || isMpfbRefit}
                onClick={() => applyColor(item.hex)} />
            ))}
          </div>
          {busy && <p role="status">Đang cập nhật màu trang phục...</p>}
          {error && <p role="alert" className="vfit-builder-error">{error}</p>}
          <p className="vfit-builder-note">Mẫu cơ thể được dựng từ thông số đã chọn, không lấy số đo từ ảnh. Bản xem trước chưa tính điểm vừa vặn hoặc gợi ý size.</p>
          <button className="vfit-btn-secondary" type="button" onClick={onTryAnotherSize}>Chọn trang phục hoặc size khác</button>
        </section>
      </div>
    </div>
  );
};
