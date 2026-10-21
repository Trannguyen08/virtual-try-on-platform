import React, { useState } from 'react';
import { bodyBuilderApi, BodyBuilderJob, BodyParameters, defaultBodyParameters } from '../../api/bodyBuilderApi';
import { BodyBuilderStep } from '../../components/tryon/BodyBuilderStep';
import { GeneratedBodyViewer } from '../../components/tryon/GeneratedBodyViewer';
import { ProcessingStep } from '../../components/tryon/ProcessingStep';
import { SelectGarmentStep } from '../../components/tryon/SelectGarmentStep';
import { UploadStep } from '../../components/tryon/UploadStep';
import { Product } from '../../data/mockProducts';

type TryOnStep = 'upload' | 'body-builder' | 'select-garment' | 'processing' | 'viewer-3d';

interface TryOnPageProps {
  initialGarment?: Product | null;
  onNavigateCatalog?: () => void;
}

export const TryOnPage: React.FC<TryOnPageProps> = ({ initialGarment }) => {
  const [currentStep, setCurrentStep] = useState<TryOnStep>(
    'upload'
  );

  const [heightCm, setHeightCm] = useState<number>(170);

  const [selectedGarment, setSelectedGarment] = useState<Product | null>(
    initialGarment || null
  );
  const [selectedSize, setSelectedSize] = useState<string>('M');

  const [processingStatus, setProcessingStatus] = useState<string>('');
  const [manualParams, setManualParams] = useState<BodyParameters | null>(null);
  const [manualBodyJob, setManualBodyJob] = useState<BodyBuilderJob | null>(null);
  const [manualClothingJob, setManualClothingJob] = useState<BodyBuilderJob | null>(null);
  const [error, setError] = useState('');

  // Ảnh chỉ được xem trước; body 3D dùng thông số MPFB, không suy từ ảnh.
  const handleUploadComplete = (height: number) => {
    setHeightCm(height);
    setManualParams(null);
    setManualBodyJob(null);
    setManualClothingJob(null);
    setError('');
    setCurrentStep('select-garment');
  };

  // Cả hai lối vào đều dùng cùng một GLB MPFB do Blender xuất.
  const handleConfirmGarment = async (garment: Product, size: string) => {
    setSelectedGarment(garment);
    setSelectedSize(size);
    setError('');
    setCurrentStep('processing');
    setProcessingStatus('Đang xử lý mô hình...');

    try {
      setProcessingStatus('Blender đang dựng body MPFB 3D...');
      const bodyJob = manualBodyJob?.method === 'blender_mpfb'
        ? manualBodyJob
        : await bodyBuilderApi.generate(manualParams || defaultBodyParameters(heightCm));
      setManualBodyJob(bodyJob);
      setProcessingStatus(garment.fittingMode === 'body_refit'
        ? 'Blender đang refit quần áo theo body MPFB...'
        : 'Blender đang tạo hình minh họa trang phục...');
      try {
        const clothingJob = await bodyBuilderApi.clothing(bodyJob.job_id, garment.id, garment.category,
          garment.colors[0]?.hex || '#ffffff', size);
        setManualClothingJob(clothingJob);
      } catch (cause) {
        setManualClothingJob(null);
        setError(cause instanceof Error ? cause.message : 'Không thể tạo trang phục');
      }
      setCurrentStep('viewer-3d');
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Không thể tạo mô hình');
      setCurrentStep('select-garment');
    }
  };

  // 3. Khởi động lại luồng từ đầu
  const handleRestart = () => {
    setCurrentStep('upload');
    setManualParams(null);
    setManualBodyJob(null);
    setManualClothingJob(null);
    setError('');
  };

  // Determine active step index for Stepper Bar
  const stepIndex =
    currentStep === 'upload' || currentStep === 'body-builder' ? 1 : currentStep === 'select-garment' ? 2 : 3;

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '1rem 0 4rem 0' }}>
      {/* Top Stepper Progression Bar */}
      {currentStep !== 'processing' && (
        <div className="vfit-stepper-container">
          <div className="vfit-stepper-track">
            {/* Step 1 */}
            <div
              className="vfit-step-item"
              onClick={() => currentStep !== 'upload' && setCurrentStep('upload')}
            >
              <div
                className={`vfit-step-circle ${
                  stepIndex === 1 ? 'active' : stepIndex > 1 ? 'completed' : ''
                }`}
              >
                {stepIndex > 1 ? '✓' : '1'}
              </div>
              <span className="vfit-step-label">Body Blender</span>
              <span className="vfit-step-sublabel">
                {stepIndex === 1 ? 'Đang thực hiện' : 'Hoàn tất'}
              </span>
            </div>

            {/* Connector 1-2 */}
            <div
              className={`vfit-step-connector ${stepIndex >= 2 ? 'filled' : ''}`}
            />

            {/* Step 2 */}
            <div
              className="vfit-step-item"
              onClick={() =>
                (currentStep === 'viewer-3d' || currentStep === 'select-garment' || manualParams) &&
                setCurrentStep('select-garment')
              }
            >
              <div
                className={`vfit-step-circle ${
                  stepIndex === 2 ? 'active' : stepIndex > 2 ? 'completed' : ''
                }`}
              >
                {stepIndex > 2 ? '✓' : '2'}
              </div>
              <span className="vfit-step-label">Chọn trang phục & Size</span>
              <span className="vfit-step-sublabel">
                {stepIndex === 2
                  ? 'Đang thực hiện'
                  : stepIndex > 2
                  ? 'Hoàn tất'
                  : 'Bước kế tiếp'}
              </span>
            </div>

            {/* Connector 2-3 */}
            <div
              className={`vfit-step-connector ${stepIndex >= 3 ? 'filled' : ''}`}
            />

            {/* Step 3 */}
            <div className="vfit-step-item">
              <div
                className={`vfit-step-circle ${stepIndex === 3 ? 'active' : ''}`}
              >
                3
              </div>
              <span className="vfit-step-label">Kết quả 3D tương tác</span>
              <span className="vfit-step-sublabel">
                {stepIndex === 3 ? 'Đang hiển thị' : 'Chờ xử lý'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Step Content */}
      {currentStep === 'upload' && (
        <UploadStep onNext={handleUploadComplete} onCreateBody={() => setCurrentStep('body-builder')} />
      )}

      {currentStep === 'body-builder' && (
        <BodyBuilderStep initialParams={manualParams} onBack={() => setCurrentStep('upload')} onNext={(params) => {
          setManualParams(params);
          setManualBodyJob(null);
          setManualClothingJob(null);
          setError('');
          setCurrentStep('select-garment');
        }} />
      )}

      {currentStep === 'select-garment' && (
        <>{error && <p role="alert" className="vfit-builder-error">{error}</p>}
        <SelectGarmentStep
          initialGarment={selectedGarment}
          onBack={() => setCurrentStep(manualParams ? 'body-builder' : 'upload')}
          onConfirm={handleConfirmGarment}
        /></>
      )}

      {currentStep === 'processing' && (
        <ProcessingStep statusMessage={processingStatus} />
      )}

      {currentStep === 'viewer-3d' && manualBodyJob && selectedGarment && (
        <GeneratedBodyViewer bodyJob={manualBodyJob} initialClothingJob={manualClothingJob}
          garment={selectedGarment} selectedSize={selectedSize} initialError={error}
          onTryAnotherSize={() => setCurrentStep('select-garment')} onRestart={handleRestart} />
      )}

    </div>
  );
};
