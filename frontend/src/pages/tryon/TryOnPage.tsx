import React, { useState } from 'react';
import { BodyData, FitResult, tryonApi } from '../../api/tryonApi';
import { ConfirmTryOnStep } from '../../components/tryon/ConfirmTryOnStep';
import { InteractiveViewer3DStep } from '../../components/tryon/InteractiveViewer3DStep';
import { ProcessingStep } from '../../components/tryon/ProcessingStep';
import { SelectGarmentStep } from '../../components/tryon/SelectGarmentStep';
import { UploadStep } from '../../components/tryon/UploadStep';
import { MOCK_PRODUCTS, Product } from '../../data/mockProducts';
import { BodyCustomParams, BODY_PRESETS } from '../../data/bodyPresets';

type TryOnStep = 'upload' | 'select-garment' | 'confirm' | 'processing' | 'viewer-3d';

interface TryOnPageProps {
  initialGarment?: Product | null;
  onNavigateCatalog?: () => void;
  onNavigateHistory?: () => void;
}

export const TryOnPage: React.FC<TryOnPageProps> = ({ initialGarment, onNavigateCatalog, onNavigateHistory }) => {
  const [currentStep, setCurrentStep] = useState<TryOnStep>(
    initialGarment ? 'select-garment' : 'upload'
  );

  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string>(
    BODY_PRESETS[0].img
  );
  const [heightCm, setHeightCm] = useState<number>(170);

  const [bodyCustomParams, setBodyCustomParams] = useState<BodyCustomParams>({
    height: 170,
    weight: 50,
    gender: 'female',
    age: 24,
    skinTone: 'light',
    skinColorHex: '#f5d0b5',
    selectedPresetId: 'slim',
    glbModelUrl: '/models/body_default.glb',
    proportions: { ...BODY_PRESETS[0].proportions },
  });

  const [selectedGarment, setSelectedGarment] = useState<Product>(
    initialGarment || MOCK_PRODUCTS[0]
  );
  const [selectedSize, setSelectedSize] = useState<string>('M');

  const [bodyData, setBodyData] = useState<BodyData | null>(null);
  const [fitResult, setFitResult] = useState<FitResult | null>(null);
  const [processingStatus, setProcessingStatus] = useState<string>('');

  // 1. Sau khi upload ảnh và nhập chiều cao ở Bước 1
  const handleUploadComplete = async (
    file: File | null,
    previewUrl: string,
    height: number,
    customParams: BodyCustomParams
  ) => {
    setPhotoFile(file);
    setPhotoPreview(previewUrl);
    setHeightCm(height);
    setBodyCustomParams(customParams);
    setCurrentStep('select-garment');
  };

  // 2. Sau khi chọn trang phục ở Bước 2 -> Chuyển sang Bước xác nhận (Confirm)
  const handleGarmentSelected = (garment: Product, size: string) => {
    setSelectedGarment(garment);
    setSelectedSize(size);
    setCurrentStep('confirm');
  };

  // 3. Sau khi người dùng xác nhận ở Bước 3 -> Chạy AI Processing
  const handleStartProcessing = async () => {
    setCurrentStep('processing');
    setProcessingStatus('Đang gửi dữ liệu ảnh và quét vóc dáng...');

    try {
      // Step A: Blender MPFB 3D Generation / Preset fallback
      setProcessingStatus('Đang đồng bộ tham số MPFB và chuẩn bị lưới 3D...');
      const blenderJob = await tryonApi.generateBodyWithBlender(bodyCustomParams, (msg) => {
        setProcessingStatus(msg);
      });

      const updatedParams: BodyCustomParams = {
        ...bodyCustomParams,
        glbModelUrl: blenderJob.glbUrl,
      };
      setBodyCustomParams(updatedParams);

      // Step B: Phân tích ảnh hoặc dùng mock
      let bodyRes = bodyData;
      if (!bodyRes) {
        setProcessingStatus('AI đang phân tích tỷ lệ cơ thể và dựng body mesh...');
        const blobOrFile = photoFile || new Blob(['mock'], { type: 'image/jpeg' });
        bodyRes = await tryonApi.analyze(blobOrFile, heightCm, updatedParams);
        setBodyData(bodyRes);
      }

      // Step C: Tạo fit job và chờ kết quả
      setProcessingStatus('Đang thực hiện draping trang phục và tính toán độ căng vải...');
      const fitRes = await tryonApi.fitAndPoll(
        bodyRes.body_id,
        selectedGarment.id,
        selectedSize,
        (msg) => setProcessingStatus(msg)
      );

      setFitResult(fitRes);
      setCurrentStep('viewer-3d');
    } catch {
      // Trường hợp có lỗi, vẫn cho phép xem mô phỏng để trải nghiệm không bị gián đoạn
      setCurrentStep('viewer-3d');
    }
  };

  // Khởi động lại luồng từ đầu
  const handleRestart = () => {
    setCurrentStep('upload');
    setFitResult(null);
  };

  // Determine active step index for Stepper Bar
  const stepIndex =
    currentStep === 'upload'
      ? 1
      : currentStep === 'select-garment'
      ? 2
      : currentStep === 'confirm'
      ? 3
      : 4;

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
              <span className="vfit-step-label">Tải ảnh chân dung</span>
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
                (currentStep === 'viewer-3d' || currentStep === 'confirm' || photoPreview) &&
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
              <span className="vfit-step-label">Chọn trang phục</span>
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

            {/* Step 3: Xác nhận */}
            <div
              className="vfit-step-item"
              onClick={() =>
                currentStep === 'viewer-3d' && setCurrentStep('confirm')
              }
            >
              <div
                className={`vfit-step-circle ${
                  stepIndex === 3 ? 'active' : stepIndex > 3 ? 'completed' : ''
                }`}
              >
                {stepIndex > 3 ? '✓' : '3'}
              </div>
              <span className="vfit-step-label">Xác nhận cấu hình</span>
              <span className="vfit-step-sublabel">
                {stepIndex === 3
                  ? 'Đang thực hiện'
                  : stepIndex > 3
                  ? 'Hoàn tất'
                  : 'Bước kế tiếp'}
              </span>
            </div>

            {/* Connector 3-4 */}
            <div
              className={`vfit-step-connector ${stepIndex >= 4 ? 'filled' : ''}`}
            />

            {/* Step 4: Kết quả */}
            <div className="vfit-step-item">
              <div
                className={`vfit-step-circle ${stepIndex === 4 ? 'active' : ''}`}
              >
                4
              </div>
              <span className="vfit-step-label">Kết quả 3D & AI 4K</span>
              <span className="vfit-step-sublabel">
                {stepIndex === 4 ? 'Đang hiển thị' : 'Chờ xử lý'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Step Content */}
      {currentStep === 'upload' && (
        <UploadStep
          initialCustomParams={bodyCustomParams}
          onNext={handleUploadComplete}
        />
      )}

      {currentStep === 'select-garment' && (
        <SelectGarmentStep
          initialGarment={selectedGarment}
          onBack={() => setCurrentStep('upload')}
          onConfirm={handleGarmentSelected}
        />
      )}

      {currentStep === 'confirm' && (
        <ConfirmTryOnStep
          photoPreview={photoPreview}
          heightCm={heightCm}
          garment={selectedGarment}
          selectedSize={selectedSize}
          customParams={bodyCustomParams}
          onBack={() => setCurrentStep('select-garment')}
          onChangeModel={() => setCurrentStep('upload')}
          onChangeGarment={() => setCurrentStep('select-garment')}
          onConfirmStart={handleStartProcessing}
        />
      )}

      {currentStep === 'processing' && (
        <ProcessingStep statusMessage={processingStatus} />
      )}

      {currentStep === 'viewer-3d' && (
        <InteractiveViewer3DStep
          garment={selectedGarment}
          selectedSize={selectedSize}
          bodyData={bodyData}
          fitResult={fitResult}
          customParams={bodyCustomParams}
          onTryAnotherSize={() => setCurrentStep('select-garment')}
          onRestart={handleRestart}
          onNavigateHistory={onNavigateHistory}
        />
      )}
    </div>
  );
};

export default TryOnPage;
