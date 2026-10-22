import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

export interface OutfitLayer { url: string; label: string; kind: 'image' | 'catalog' }

function disposeObject(object: THREE.Object3D) {
  const textures = new Set<THREE.Texture>();
  object.traverse((node) => {
    if (!(node instanceof THREE.Mesh)) return;
    node.geometry.dispose();
    const materials = Array.isArray(node.material) ? node.material : [node.material];
    materials.forEach((material) => {
      Object.values(material).forEach((value) => { if (value instanceof THREE.Texture) textures.add(value); });
      material.dispose();
    });
  });
  textures.forEach((texture) => texture.dispose());
}

/** Compose in the exported metre/Y-up frame; never center or scale each garment. */
export function OutfitViewer({ bodyUrl, layers }: { bodyUrl: string; layers: OutfitLayer[] }) {
  const mount = useRef<HTMLDivElement>(null);
  const orbitRef = useRef<OrbitControls | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [rotate, setRotate] = useState(false);
  const rotateRef = useRef(rotate);
  rotateRef.current = rotate;
  // Parent creates small descriptors on render; only reload when asset identities change.
  const layerKey = JSON.stringify(layers);

  useEffect(() => {
    const container = mount.current;
    if (!container) return;
    let cancelled = false;
    let renderer: THREE.WebGLRenderer;
    setError(''); setLoading(true);
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    } catch {
      setError('Không mở được chế độ 3D. Kiểm tra WebGL hoặc thử trình duyệt khác.');
      setLoading(false);
      return;
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    container.appendChild(renderer.domElement);
    const scene = new THREE.Scene();
    const group = new THREE.Group();
    scene.add(group, new THREE.HemisphereLight(0xffffff, 0xb3b5cd, 2.2));
    const key = new THREE.DirectionalLight(0xffffff, 2.5);
    key.position.set(3, 5, 4); scene.add(key);
    const camera = new THREE.PerspectiveCamera(38, 1, 0.01, 100);
    camera.position.set(0, 0.9, 3.5);
    const orbit = new OrbitControls(camera, renderer.domElement);
    orbitRef.current = orbit;
    orbit.enableDamping = true; orbit.enablePan = false;
    orbit.minDistance = 0.8; orbit.maxDistance = 7;
    orbit.target.set(0, 0.9, 0);
    const resize = () => {
      const width = container.clientWidth || 400;
      const height = container.clientHeight || 560;
      renderer.setSize(width, height);
      camera.aspect = width / height; camera.updateProjectionMatrix();
    };
    const observer = new ResizeObserver(resize); observer.observe(container); resize();
    const loader = new GLTFLoader();
    const load = async () => {
      const base = await loader.loadAsync(bodyUrl);
      if (cancelled) { disposeObject(base.scene); return; }
      group.add(base.scene);
      const bodyNames = new Set<string>();
      base.scene.traverse((node) => { if (node instanceof THREE.Mesh) bodyNames.add(node.name); });
      if (!bodyNames.size) throw new Error('Model cơ thể không có mesh hợp lệ. Hãy tạo lại model.');
      const bounds = new THREE.Box3().setFromObject(base.scene);
      const center = bounds.getCenter(new THREE.Vector3());
      const height = bounds.max.y - bounds.min.y;
      group.position.set(-center.x, -bounds.min.y, -center.z);
      orbit.target.set(0, height / 2, 0);
      camera.position.set(0, height / 2, Math.max(2.5, height * 1.8));
      orbit.update(); orbit.saveState();
      for (const layer of JSON.parse(layerKey) as OutfitLayer[]) {
        const gltf = await loader.loadAsync(layer.url);
        if (cancelled) { disposeObject(gltf.scene); return; }
        // Image composer exports GarmentFront/Back/Sides; native catalog retains body names.
        let garmentCount = 0;
        let matchedBodyCount = 0;
        gltf.scene.traverse((node) => {
          if (!(node instanceof THREE.Mesh)) return;
          const isBody = bodyNames.has(node.name);
          if (isBody) matchedBodyCount++;
          const isGarment = layer.kind === 'image' ? /^Garment/.test(node.name) : !isBody;
          // MHCLO garments can be children of the human mesh. Hiding that parent
          // would hide the clothing too; render layers exclude only the body draw.
          node.layers.set(isGarment ? 0 : 1);
          if (isGarment) garmentCount++;
        });
        if (!garmentCount || (layer.kind === 'catalog' && !matchedBodyCount)) {
          disposeObject(gltf.scene);
          throw new Error(`Không xác định được lớp trang phục của ${layer.label}. Cần kiểm tra cấu trúc GLB với backend.`);
        }
        group.add(gltf.scene);
      }
    };
    void load().catch((reason: unknown) => {
      if (!cancelled) {
        // Keep the body available while making an incomplete outfit explicit.
        setError(reason instanceof Error ? reason.message : 'Không tải được trang phục 3D.');
      }
    }).finally(() => { if (!cancelled) setLoading(false); });
    let frame = 0;
    const animate = () => {
      frame = requestAnimationFrame(animate);
      orbit.autoRotate = rotateRef.current; orbit.update(); renderer.render(scene, camera);
    };
    animate();
    const contextLost = (event: Event) => {
      event.preventDefault(); setError('Kết nối WebGL bị gián đoạn. Tải lại trang để mở lại mô hình.');
    };
    renderer.domElement.addEventListener('webglcontextlost', contextLost);
    return () => {
      cancelled = true; cancelAnimationFrame(frame); observer.disconnect(); orbit.dispose();
      orbitRef.current = null; disposeObject(scene);
      renderer.domElement.removeEventListener('webglcontextlost', contextLost);
      renderer.dispose(); renderer.domElement.remove();
    };
  }, [bodyUrl, layerKey]);

  return <div className="outfit-viewer">
    <div ref={mount} className="outfit-viewer-canvas" aria-label="Model 3D, kéo để xoay và cuộn để phóng to" />
    {loading && <p className="outfit-viewer-status" role="status">Đang tải model 3D…</p>}
    {error && <p className="outfit-error" role="alert">{error} Bộ đồ có thể chưa hiển thị đầy đủ.</p>}
    <div className="outfit-viewer-controls">
      <button type="button" aria-pressed={rotate} onClick={() => setRotate(!rotate)}>{rotate ? 'Dừng xoay' : 'Xoay 360°'}</button>
      <button type="button" onClick={() => orbitRef.current?.reset()}>Góc ban đầu</button>
      <span>Kéo để xoay · Cuộn để zoom</span>
    </div>
  </div>;
}
