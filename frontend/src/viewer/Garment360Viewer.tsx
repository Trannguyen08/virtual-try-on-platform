import React, { Suspense, useEffect, useRef, useState } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { Bounds, Center, Html, OrbitControls, useGLTF } from '@react-three/drei';
import { GarmentViewerAnnotation } from './garmentAnnotations';

type ViewPreset = 'default' | 'front' | 'back' | 'left' | 'right';

const VIEW_POSITIONS: Record<ViewPreset, [number, number, number]> = {
  default: [1.7, 0.7, 2.5],
  front: [0, 0.3, 2.7],
  back: [0, 0.3, -2.7],
  left: [-2.7, 0.3, 0],
  right: [2.7, 0.3, 0],
};

function GarmentModel({
  url,
  scale,
  annotationMode,
  annotations,
  annotationSide,
}: {
  url: string;
  scale: [number, number, number];
  annotationMode: boolean;
  annotations: GarmentViewerAnnotation[];
  annotationSide: 'front' | 'back';
}) {
  const gltf = useGLTF(url);
  useEffect(
    () => () => {
      useGLTF.clear(url);
    },
    [url],
  );
  return (
    <Bounds fit clip observe margin={1.25}>
      <Center>
        <group scale={scale}>
          <primitive object={gltf.scene} />
          {annotationMode && annotations.map((annotation) => {
            const sourcePosition = annotationSide === 'back'
              ? annotation.backPosition
              : annotation.frontPosition;
            const position: [number, number, number] = [
              sourcePosition[0],
              sourcePosition[1],
              sourcePosition[2] + (annotationSide === 'back' ? -0.01 : 0.01),
            ];
            return (
              <Html key={annotation.id} position={position} center occlude>
                <span
                  className={`g3d-landmark${annotation.estimated ? ' g3d-landmark--estimated' : ''}`}
                  title={`Vùng cơ thể tương ứng: ${annotation.bodyRegion}`}
                >
                  <i aria-hidden="true" />
                  {annotation.label}
                </span>
              </Html>
            );
          })}
        </group>
      </Center>
    </Bounds>
  );
}

function ViewerControls({
  preset,
  autoRotate,
  onInteract,
}: {
  preset: ViewPreset;
  autoRotate: boolean;
  onInteract: () => void;
}) {
  const { camera } = useThree();
  const controlsRef = useRef<any>(null);

  useEffect(() => {
    const position = VIEW_POSITIONS[preset];
    camera.position.set(...position);
    camera.lookAt(0, 0, 0);
    controlsRef.current?.target.set(0, 0, 0);
    controlsRef.current?.update();
  }, [camera, preset]);

  return (
    <OrbitControls
      ref={controlsRef}
      makeDefault
      enableDamping
      enablePan={false}
      autoRotate={autoRotate}
      autoRotateSpeed={1.5}
      minDistance={0.5}
      maxDistance={8}
      onStart={onInteract}
    />
  );
}

export const Garment360Viewer: React.FC<{
  modelUrl: string;
  subject?: 'body' | 'garment';
  thumbnailUrl?: string | null;
  scale?: [number, number, number];
  annotations?: GarmentViewerAnnotation[];
}> = ({
  modelUrl,
  subject = 'garment',
  thumbnailUrl,
  scale = [1, 1, 1],
  annotations = [],
}) => {
  const [autoRotate, setAutoRotate] = useState(true);
  const [canvasFailed, setCanvasFailed] = useState(false);
  const [preset, setPreset] = useState<ViewPreset>('default');
  const [annotationMode, setAnnotationMode] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  if (canvasFailed && thumbnailUrl) {
    return <img
      src={thumbnailUrl}
      alt={subject === 'body' ? 'Bản xem trước body 3D' : 'Bản xem trước trang phục 3D'}
      className="g3d-viewer__fallback"
    />;
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
          <Suspense fallback={null}>
            <GarmentModel
              url={modelUrl}
              scale={scale}
              annotationMode={annotationMode}
              annotations={annotations}
              annotationSide={preset === 'back' ? 'back' : 'front'}
            />
          </Suspense>
          <ViewerControls
            preset={preset}
            autoRotate={autoRotate}
            onInteract={() => setAutoRotate(false)}
          />
        </Canvas>
      </div>
      <div className="g3d-viewer__controls">
        <div className="g3d-viewer__mode-switch" role="group" aria-label={subject === 'body' ? 'Chế độ xem body 3D' : 'Chế độ xem trang phục'}>
          <button
            className={`g3d-button ${annotationMode ? 'g3d-button--secondary' : 'g3d-button--primary'}`}
            type="button"
            aria-pressed={!annotationMode}
            onClick={() => setAnnotationMode(false)}
          >
            Xem 3D
          </button>
          {subject === 'garment' && (
            <button
              className={`g3d-button ${annotationMode ? 'g3d-button--primary' : 'g3d-button--secondary'}`}
              type="button"
              disabled={!annotations.length}
              aria-pressed={annotationMode}
              onClick={() => setAnnotationMode(true)}
            >
              Vùng cơ thể
            </button>
          )}
        </div>
        {annotationMode && (
          <p className="g3d-viewer__annotation-note">
            Chỉ hiển thị các điểm có thể suy ra từ ảnh trang phục. Những bộ phận không thấy rõ trong ảnh sẽ được ẩn;
            vị trí này chưa xác nhận độ vừa với body mesh.
          </p>
        )}
        {(['front', 'back', 'left', 'right'] as ViewPreset[]).map((view) => (
          <button
            key={view}
            className="g3d-button g3d-button--secondary"
            type="button"
            onClick={() => {
              setAutoRotate(false);
              setPreset(view);
            }}
          >
            {{
              default: 'Mặc định',
              front: 'Mặt trước',
              back: 'Mặt sau',
              left: 'Bên trái',
              right: 'Bên phải',
            }[view]}
          </button>
        ))}
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
          onClick={() => {
            setAutoRotate(false);
            setPreset('default');
          }}
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
