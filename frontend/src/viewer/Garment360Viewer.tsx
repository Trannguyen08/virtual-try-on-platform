import React, { Suspense, useEffect, useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { Bounds, Center, OrbitControls, useGLTF } from '@react-three/drei';

function GarmentModel({ url }: { url: string }) {
  const gltf = useGLTF(url);
  useEffect(
    () => () => {
      useGLTF.clear(url);
    },
    [url],
  );
  return (
    <Bounds fit clip observe margin={1.25}>
      <Center><primitive object={gltf.scene} /></Center>
    </Bounds>
  );
}

export const Garment360Viewer: React.FC<{ modelUrl: string; thumbnailUrl?: string | null }> = ({
  modelUrl,
  thumbnailUrl,
}) => {
  const [autoRotate, setAutoRotate] = useState(true);
  const [canvasFailed, setCanvasFailed] = useState(false);
  const [viewKey, setViewKey] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  if (canvasFailed && thumbnailUrl) {
    return <img src={thumbnailUrl} alt="Bản xem trước trang phục 3D" className="g3d-viewer__fallback" />;
  }
  return (
    <section className="g3d-viewer">
      <div ref={containerRef} className="g3d-viewer__canvas">
        <Canvas
          camera={{ position: [0, 0.5, 2.5], fov: 40 }}
          gl={{ antialias: true, alpha: true }}
          onCreated={({ gl }) => {
            gl.domElement.addEventListener('webglcontextlost', () => setCanvasFailed(true), {
              once: true,
            });
          }}
        >
          <ambientLight intensity={1.3} />
          <directionalLight position={[3, 4, 5]} intensity={2.2} />
          <directionalLight position={[-3, 2, -4]} intensity={1.0} />
          <Suspense fallback={null}><GarmentModel url={modelUrl} /></Suspense>
          <OrbitControls
            key={viewKey}
            makeDefault
            enableDamping
            enablePan={false}
            autoRotate={autoRotate}
            autoRotateSpeed={1.5}
            minDistance={0.5}
            maxDistance={8}
            onStart={() => setAutoRotate(false)}
          />
        </Canvas>
      </div>
      <div className="g3d-viewer__controls">
        <button
          className="g3d-button g3d-button--secondary"
          type="button"
          onClick={() => setAutoRotate((value) => !value)}
        >
          {autoRotate ? 'Dừng tự xoay' : 'Bật tự xoay'}
        </button>
        <button
          className="g3d-button g3d-button--secondary"
          type="button"
          onClick={() => setViewKey((value) => value + 1)}
        >
          Đặt lại góc nhìn
        </button>
        <button
          className="g3d-button g3d-button--secondary"
          type="button"
          onClick={() => void containerRef.current?.requestFullscreen()}
        >
          Toàn màn hình
        </button>
      </div>
    </section>
  );
};
