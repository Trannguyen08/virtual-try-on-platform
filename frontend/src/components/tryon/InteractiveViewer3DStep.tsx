import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { BodyData, FitResult } from '../../api/tryonApi';
import { Product } from '../../data/mockProducts';
import { historyStorage } from '../../services/historyStorage';
import { TryOnHistoryItem } from '../../data/mockHistory';

interface InteractiveViewer3DStepProps {
  garment: Product;
  selectedSize: string;
  bodyData: BodyData | null;
  fitResult: FitResult | null;
  onTryAnotherSize: () => void;
  onRestart: () => void;
  onNavigateHistory?: () => void;
}

export const InteractiveViewer3DStep: React.FC<InteractiveViewer3DStepProps> = ({
  garment,
  selectedSize,
  bodyData,
  fitResult,
  onTryAnotherSize,
  onRestart,
  onNavigateHistory,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [activeLayer, setActiveLayer] = useState<'both' | 'body' | 'garment'>('both');
  const [isWireframe, setIsWireframe] = useState<boolean>(false);
  const [isAutoRotate, setIsAutoRotate] = useState<boolean>(true);
  const [addedToCart, setAddedToCart] = useState<boolean>(false);
  const [savedToHistory, setSavedToHistory] = useState<boolean>(false);

  // References for Three.js state
  const sceneRef = useRef<THREE.Scene | null>(null);
  const avatarGroupRef = useRef<THREE.Group | null>(null);
  const bodyMeshGroupRef = useRef<THREE.Group | null>(null);
  const garmentMeshGroupRef = useRef<THREE.Group | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);

  // Initialize Three.js interactive canvas
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth || 600;
    const height = container.clientHeight || 600;

    // 1. Scene & Camera
    const scene = new THREE.Scene();
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 1.15, 3.1);
    cameraRef.current = camera;

    // 2. Renderer
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.shadowMap.enabled = true;
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // 3. Lighting
    const ambientLight = new THREE.AmbientLight(0xfff5fa, 1.5);
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 1.8);
    keyLight.position.set(2, 4, 3);
    keyLight.castShadow = true;
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0xd4e2ff, 1.2);
    fillLight.position.set(-3, 2, -1);
    scene.add(fillLight);

    const rimLight = new THREE.DirectionalLight(0xe8d0ff, 1.4);
    rimLight.position.set(0, 3, -3);
    scene.add(rimLight);

    // 4. Avatar Groups
    const avatarGroup = new THREE.Group();
    const bodyMeshGroup = new THREE.Group();
    const garmentMeshGroup = new THREE.Group();

    avatarGroupRef.current = avatarGroup;
    bodyMeshGroupRef.current = bodyMeshGroup;
    garmentMeshGroupRef.current = garmentMeshGroup;

    avatarGroup.add(bodyMeshGroup);
    avatarGroup.add(garmentMeshGroup);
    scene.add(avatarGroup);

    // 5. Materials
    const skinMaterial = new THREE.MeshStandardMaterial({
      color: 0xf5d0b5,
      roughness: 0.6,
      metalness: 0.05,
      wireframe: isWireframe,
    });

    const garmentMaterial = new THREE.MeshStandardMaterial({
      color: garment.colors[0]?.hex ? parseInt(garment.colors[0].hex.replace('#', '0x')) : 0x080a61,
      roughness: 0.8,
      metalness: 0.04,
      wireframe: isWireframe,
    });

    const pantsMaterial = new THREE.MeshStandardMaterial({
      color: 0x242d3d,
      roughness: 0.85,
      metalness: 0.02,
      wireframe: isWireframe,
    });

    // 6. Build Stylized 3D Avatar (Head, Neck, Arms, Legs)
    // Head
    const headGeo = new THREE.SphereGeometry(0.17, 32, 32);
    headGeo.scale(0.85, 1.15, 0.95);
    const head = new THREE.Mesh(headGeo, skinMaterial);
    head.position.y = 1.95;
    bodyMeshGroup.add(head);

    // Neck
    const neckGeo = new THREE.CylinderGeometry(0.065, 0.08, 0.16, 20);
    const neck = new THREE.Mesh(neckGeo, skinMaterial);
    neck.position.y = 1.76;
    bodyMeshGroup.add(neck);

    // Body Core Underlay
    const torsoGeo = new THREE.CylinderGeometry(0.22, 0.2, 0.5, 24);
    torsoGeo.scale(1.05, 1, 0.65);
    const innerTorso = new THREE.Mesh(torsoGeo, skinMaterial);
    innerTorso.position.y = 1.42;
    bodyMeshGroup.add(innerTorso);

    // Arms
    [-1, 1].forEach((side) => {
      const armGeo = new THREE.CylinderGeometry(0.055, 0.048, 0.55, 18);
      const arm = new THREE.Mesh(armGeo, skinMaterial);
      arm.rotation.z = side * 0.14;
      arm.position.set(side * 0.33, 1.25, 0);
      bodyMeshGroup.add(arm);
    });

    // Legs / Pants
    [-1, 1].forEach((side) => {
      const legGeo = new THREE.CylinderGeometry(0.08, 0.065, 0.92, 20);
      const leg = new THREE.Mesh(legGeo, pantsMaterial);
      leg.position.set(side * 0.13, 0.68, 0);
      bodyMeshGroup.add(leg);
    });

    // 7. Build Garment Mesh (Upper Torso, Collar, Sleeves)
    // Upper Chest Garment
    const garmentTorsoGeo = new THREE.CylinderGeometry(0.245, 0.23, 0.54, 28);
    garmentTorsoGeo.scale(1.1, 1, 0.7);
    const garmentTorso = new THREE.Mesh(garmentTorsoGeo, garmentMaterial);
    garmentTorso.position.y = 1.44;
    garmentMeshGroup.add(garmentTorso);

    // Collar
    const collarGeo = new THREE.TorusGeometry(0.09, 0.018, 16, 32);
    const collar = new THREE.Mesh(collarGeo, garmentMaterial);
    collar.rotation.x = Math.PI / 2;
    collar.position.y = 1.68;
    garmentMeshGroup.add(collar);

    // Sleeves
    [-1, 1].forEach((side) => {
      const sleeveGeo = new THREE.CylinderGeometry(0.08, 0.085, 0.24, 18);
      const sleeve = new THREE.Mesh(sleeveGeo, garmentMaterial);
      sleeve.rotation.z = side * 0.28;
      sleeve.position.set(side * 0.29, 1.55, 0);
      garmentMeshGroup.add(sleeve);
    });

    // 8. Mouse drag interaction for 360° rotation
    let isDragging = false;
    let prevMouseX = 0;

    const onMouseDown = (e: MouseEvent) => {
      isDragging = true;
      prevMouseX = e.clientX;
    };

    const onMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const deltaX = e.clientX - prevMouseX;
      avatarGroup.rotation.y += deltaX * 0.01;
      prevMouseX = e.clientX;
    };

    const onMouseUp = () => {
      isDragging = false;
    };

    container.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);

    // 9. Render Loop
    let animationFrameId: number;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);

      if (isAutoRotate && !isDragging) {
        avatarGroup.rotation.y += 0.005;
      }

      renderer.render(scene, camera);
    };
    animate();

    // Resize handler
    const handleResize = () => {
      if (!container) return;
      const newW = container.clientWidth || 600;
      const newH = container.clientHeight || 600;
      camera.aspect = newW / newH;
      camera.updateProjectionMatrix();
      renderer.setSize(newW, newH);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      container.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
    };
  }, [garment, isWireframe, isAutoRotate]);

  // Update layer visibility
  useEffect(() => {
    if (bodyMeshGroupRef.current && garmentMeshGroupRef.current) {
      if (activeLayer === 'both') {
        bodyMeshGroupRef.current.visible = true;
        garmentMeshGroupRef.current.visible = true;
      } else if (activeLayer === 'body') {
        bodyMeshGroupRef.current.visible = true;
        garmentMeshGroupRef.current.visible = false;
      } else if (activeLayer === 'garment') {
        bodyMeshGroupRef.current.visible = false;
        garmentMeshGroupRef.current.visible = true;
      }
    }
  }, [activeLayer]);

  // Viewport Actions
  const handleZoom = (delta: number) => {
    if (cameraRef.current) {
      cameraRef.current.position.z = Math.max(1.8, Math.min(4.5, cameraRef.current.position.z + delta));
    }
  };

  const handleResetCamera = () => {
    if (cameraRef.current && avatarGroupRef.current) {
      cameraRef.current.position.set(0, 1.15, 3.1);
      avatarGroupRef.current.rotation.set(0, 0, 0);
    }
  };

  const overallLabel = fitResult?.overall.label || 'good';
  const overallScore = fitResult?.overall.score ?? 95;

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Banner Status */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: 'var(--vfit-surface-card)',
          padding: '1rem 1.75rem',
          borderRadius: 'var(--vfit-radius-xl)',
          boxShadow: '0 2px 10px rgba(8, 10, 97, 0.03)',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <button
            type="button"
            onClick={onRestart}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--vfit-secondary)',
              fontWeight: 700,
              fontSize: '0.875rem',
              cursor: 'pointer',
            }}
          >
            ← Bắt đầu lượt mới
          </button>
          <span style={{ color: 'var(--vfit-outline)' }}>|</span>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--vfit-primary-container)', margin: 0 }}>
            KẾT QUẢ THỬ ĐỒ 3D — 360° INTERACTIVE FIT
          </h2>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              backgroundColor: '#d1fae5',
              color: '#065f46',
              padding: '0.25rem 0.75rem',
              borderRadius: '9999px',
              fontSize: '0.785rem',
              fontWeight: 700,
            }}
          >
            <span className="vfit-pulse-dot" />
            Khớp phom chuẩn 99.4%
          </span>
        </div>
      </div>

      {/* Main Two-Column Viewport: 3D Canvas (Left) & Biomechanical Fit Intel (Right) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '2rem', alignItems: 'start' }}>
        {/* Left Column: 3D Canvas Container */}
        <div>
          <div className="vfit-3d-viewport-box">
            {/* Layer Visibility Pills */}
            <div className="vfit-3d-layer-pills">
              <button
                type="button"
                className={`vfit-layer-btn ${activeLayer === 'both' ? 'active' : ''}`}
                onClick={() => setActiveLayer('both')}
              >
                Cả hai
              </button>
              <button
                type="button"
                className={`vfit-layer-btn ${activeLayer === 'body' ? 'active' : ''}`}
                onClick={() => setActiveLayer('body')}
              >
                Cơ thể
              </button>
              <button
                type="button"
                className={`vfit-layer-btn ${activeLayer === 'garment' ? 'active' : ''}`}
                onClick={() => setActiveLayer('garment')}
              >
                Trang phục
              </button>
            </div>

            {/* Hint overlay */}
            <div
              style={{
                position: 'absolute',
                top: '1rem',
                left: '1rem',
                backgroundColor: 'rgba(2, 4, 9, 0.65)',
                backdropFilter: 'blur(6px)',
                color: '#ffffff',
                padding: '0.35rem 0.75rem',
                borderRadius: '9999px',
                fontSize: '0.75rem',
                pointerEvents: 'none',
                zIndex: 10,
              }}
            >
              🖱️ Giữ chuột kéo để xoay 360°
            </div>

            {/* Canvas Mount Container */}
            <div ref={mountRef} style={{ width: '100%', height: '100%', cursor: 'grab' }} />

            {/* Floating Controls Toolbar */}
            <div className="vfit-3d-floating-toolbar">
              <button
                type="button"
                className="vfit-icon-btn"
                title="Phóng to"
                onClick={() => handleZoom(-0.3)}
                style={{ width: '2rem', height: '2rem' }}
              >
                ➕
              </button>
              <button
                type="button"
                className="vfit-icon-btn"
                title="Thu nhỏ"
                onClick={() => handleZoom(0.3)}
                style={{ width: '2rem', height: '2rem' }}
              >
                ➖
              </button>
              <button
                type="button"
                className="vfit-icon-btn"
                title="Đặt lại góc nhìn"
                onClick={handleResetCamera}
                style={{ width: '2rem', height: '2rem' }}
              >
                🔄
              </button>
              <button
                type="button"
                className={`vfit-tab-btn ${isAutoRotate ? 'active' : ''}`}
                style={{ padding: '0.25rem 0.65rem', fontSize: '0.75rem' }}
                onClick={() => setIsAutoRotate(!isAutoRotate)}
              >
                Tự xoay
              </button>
              <button
                type="button"
                className={`vfit-tab-btn ${isWireframe ? 'active' : ''}`}
                style={{ padding: '0.25rem 0.65rem', fontSize: '0.75rem' }}
                onClick={() => setIsWireframe(!isWireframe)}
              >
                Khung lưới
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Biomechanical Tension & Fit Intel */}
        <div>
          <div style={{ backgroundColor: 'var(--vfit-surface-card)', borderRadius: 'var(--vfit-radius-xl)', padding: '2rem', boxShadow: '0 2px 12px rgba(8, 10, 97, 0.04)' }}>
            {/* Header Product & Size */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', paddingBottom: '1.25rem', borderBottom: '1px solid var(--vfit-surface-container-highest)' }}>
              <div>
                <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--vfit-secondary)', letterSpacing: '0.05em' }}>
                  {garment.categoryLabel} • {garment.material}
                </span>
                <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--vfit-on-surface)', margin: '0.2rem 0' }}>
                  {garment.name}
                </h3>
                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--vfit-primary-container)' }}>
                  {garment.price.toLocaleString('vi-VN')}₫
                </div>
              </div>

              {/* Selected Size Badge */}
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--vfit-secondary)', display: 'block' }}>Size đang thử</span>
                <span style={{ display: 'inline-block', backgroundColor: 'var(--vfit-primary-container)', color: '#ffffff', fontWeight: 800, fontSize: '1.25rem', padding: '0.2rem 0.85rem', borderRadius: '0.5rem', marginTop: '0.2rem' }}>
                  {selectedSize}
                </span>
              </div>
            </div>

            {/* Size Recommendation Highlight Banner */}
            <div
              style={{
                margin: '1.5rem 0',
                padding: '1.25rem',
                borderRadius: 'var(--vfit-radius-lg)',
                background: 'linear-gradient(135deg, var(--vfit-secondary-container) 0%, var(--vfit-accent-lavender) 100%)',
                border: '1px solid rgba(61, 126, 255, 0.2)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--vfit-on-primary-fixed-variant)', letterSpacing: '0.05em' }}>
                  Khuyến nghị kích thước từ AI
                </span>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--vfit-primary-container)', marginTop: '0.2rem' }}>
                  Size {fitResult?.recommendation.size || 'M'} phù hợp nhất
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--vfit-secondary)', marginTop: '0.2rem' }}>
                  Độ căng sợi vải phân bổ đồng đều ở ngực và eo
                </div>
              </div>

              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--vfit-dark-primary)' }}>
                  {overallScore}/100
                </div>
                <span className={`vfit-zone-chip ${overallLabel}`}>
                  {overallLabel === 'good' ? 'Vừa vặn' : overallLabel === 'tight' ? 'Hơi chật' : 'Hơi rộng'}
                </span>
              </div>
            </div>

            {/* 4 Anatomical Tension Zones */}
            <div style={{ marginBottom: '1.5rem' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--vfit-on-surface)', letterSpacing: '0.05em', display: 'block', marginBottom: '0.85rem' }}>
                Đánh giá áp lực vải 4 vùng cơ thể:
              </span>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem' }}>
                {[
                  { key: 'chest', label: 'Ngực (Chest)', val: bodyData?.measurements.chest_cm || 96 },
                  { key: 'waist', label: 'Eo (Waist)', val: bodyData?.measurements.waist_cm || 80 },
                  { key: 'hip', label: 'Hông (Hip)', val: bodyData?.measurements.hip_cm || 98 },
                  { key: 'shoulder', label: 'Vai (Shoulder)', val: bodyData?.measurements.shoulder_width_cm || 44 },
                ].map((zone) => {
                  const regionFit = fitResult?.regions.find((r) => r.region === zone.key);
                  const label = regionFit?.label || overallLabel;
                  return (
                    <div
                      key={zone.key}
                      style={{
                        padding: '0.85rem',
                        borderRadius: 'var(--vfit-radius-md)',
                        backgroundColor: 'var(--vfit-surface-container-low)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                      }}
                    >
                      <div>
                        <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--vfit-on-surface)' }}>
                          {zone.label}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--vfit-secondary)' }}>
                          {zone.val} cm
                        </div>
                      </div>
                      <span className={`vfit-zone-chip ${label}`}>
                        {label === 'good' ? 'Chuẩn form' : label === 'tight' ? 'Chật' : 'Rộng'}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* CTA Buttons */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1.5rem' }}>
              <button
                type="button"
                className="vfit-btn-primary"
                style={{ height: '3.25rem', fontSize: '0.95rem' }}
                onClick={() => setAddedToCart(true)}
              >
                {addedToCart ? (
                  <span>✓ ĐÃ THÊM VÀO GIỎ HÀNG (SIZE {selectedSize})</span>
                ) : (
                  <span>THÊM VÀO GIỎ HÀNG (SIZE {selectedSize})</span>
                )}
              </button>

              {/* Save To History Button */}
              <button
                type="button"
                className="vfit-btn-secondary"
                style={{
                  width: '100%',
                  justifyContent: 'center',
                  backgroundColor: savedToHistory ? 'var(--vfit-secondary-container)' : '#fff',
                  borderColor: savedToHistory ? 'var(--vfit-focus-ring)' : 'var(--vfit-border-subtle)',
                  color: savedToHistory ? 'var(--vfit-primary-container)' : 'var(--vfit-on-surface)',
                  fontWeight: 700,
                }}
                onClick={() => {
                  if (savedToHistory && onNavigateHistory) {
                    onNavigateHistory();
                    return;
                  }
                  const newItem: TryOnHistoryItem = {
                    id: `hist-${Date.now()}`,
                    productId: garment.id,
                    productName: garment.name,
                    category: garment.category,
                    categoryLabel: garment.categoryLabel,
                    price: garment.price,
                    formattedPrice: `${garment.price.toLocaleString('vi-VN')}₫`,
                    size: selectedSize,
                    colorName: garment.colors[0]?.name || 'Mặc định',
                    colorHex: garment.colors[0]?.hex || '#080a61',
                    date: new Date().toLocaleDateString('vi-VN', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    }),
                    timestamp: Date.now(),
                    originalPhotoUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=800&auto=format&fit=crop&q=80',
                    resultPhotoUrl: garment.imageUrl,
                    fitScore: overallScore,
                    inCart: addedToCart,
                    regions: {
                      chest: { score: 98, label: 'good', text: 'Chuẩn form' },
                      waist: { score: 99, label: 'good', text: 'Chuẩn form' },
                      hip: { score: 97, label: 'good', text: 'Vừa vặn' },
                      shoulder: { score: 100, label: 'good', text: 'Khớp vai hoàn hảo' },
                    },
                    notes: `Thử đồ 3D với vóc dáng ${bodyData?.measurements.chest_cm || 96}cm ngực, ${bodyData?.measurements.waist_cm || 80}cm eo.`,
                  };
                  historyStorage.saveItem(newItem);
                  setSavedToHistory(true);
                }}
              >
                {savedToHistory ? (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    ✓ ĐÃ LƯU KẾT QUẢ • XEM LỊCH SỬ THỬ ĐỒ →
                  </span>
                ) : (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                      <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                      <polyline points="17 21 17 13 7 13 7 21" />
                      <polyline points="7 3 7 8 15 8" />
                    </svg>
                    LƯU VÀO LỊCH SỬ THỬ ĐỒ
                  </span>
                )}
              </button>

              <button
                type="button"
                className="vfit-btn-secondary"
                style={{ width: '100%', justifyContent: 'center' }}
                onClick={onTryAnotherSize}
              >
                Thử với kích cỡ khác (S, L, XL)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
