import React, { useState } from 'react';
import { BodyData, FitResult, tryonApi } from '../../api/tryonApi';
import { InteractiveViewer3DStep } from '../../components/tryon/InteractiveViewer3DStep';
import { ProcessingStep } from '../../components/tryon/ProcessingStep';
import { SelectGarmentStep } from '../../components/tryon/SelectGarmentStep';
import { UploadStep } from '../../components/tryon/UploadStep';
import { MOCK_PRODUCTS, Product } from '../../data/mockProducts';

type TryOnStep = 'upload' | 'select-garment' | 'processing' | 'viewer-3d';

interface TryOnPageProps {
  initialGarment?: Product | null;
  onNavigateCatalog?: () => void;
}

export const TryOnPage: React.FC<TryOnPageProps> = ({ initialGarment }) => {
  const [currentStep, setCurrentStep] = useState<TryOnStep>(
    initialGarment ? 'select-garment' : 'upload'
  );

  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string>('');
  const [heightCm, setHeightCm] = useState<number>(170);

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
    height: number
  ) => {
    setPhotoFile(file);
    setPhotoPreview(previewUrl);
    setHeightCm(height);
    setCurrentStep('select-garment');
  };

  // 2. Sau khi xác nhận chọn đồ và size ở Bước 2 -> Bắt đầu xử lý AI
  const handleConfirmGarment = async (garment: Product, size: string) => {
    setSelectedGarment(garment);
    setSelectedSize(size);
    setCurrentStep('processing');
    setProcessingStatus('Đang gửi dữ liệu ảnh và quét vóc dáng...');

    try {
      // Step A: Phân tích ảnh hoặc dùng mock
      let bodyRes = bodyData;
      if (!bodyRes) {
        setProcessingStatus('AI đang phân tích tỷ lệ cơ thể và dựng body mesh...');
        const blobOrFile = photoFile || new Blob(['mock'], { type: 'image/jpeg' });
        bodyRes = await tryonApi.analyze(blobOrFile, heightCm);
        setBodyData(bodyRes);
      }

      // Step B: Tạo fit job và chờ kết quả
      setProcessingStatus('Đang thực hiện draping trang phục và tính toán độ căng vải...');
      const fitRes = await tryonApi.fitAndPoll(
        bodyRes.body_id,
        garment.id,
        size,
        (msg) => setProcessingStatus(msg)
      );

      setFitResult(fitRes);
      setCurrentStep('viewer-3d');
    } catch {
      // Trường hợp có lỗi, vẫn cho phép xem mô phỏng để trải nghiệm không bị gián đoạn
      setCurrentStep('viewer-3d');
    }
  };

  // 3. Khởi động lại luồng từ đầu
  const handleRestart = () => {
    setCurrentStep('upload');
    setFitResult(null);
  };

  // Determine active step index for Stepper Bar
  const stepIndex =
    currentStep === 'upload' ? 1 : currentStep === 'select-garment' ? 2 : 3;

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
                (currentStep === 'viewer-3d' || photoPreview) &&
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
        <UploadStep onNext={handleUploadComplete} />
      )}

      {currentStep === 'select-garment' && (
        <SelectGarmentStep
          initialGarment={selectedGarment}
          onBack={() => setCurrentStep('upload')}
          onConfirm={handleConfirmGarment}
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
          onTryAnotherSize={() => setCurrentStep('select-garment')}
          onRestart={handleRestart}
        />
      )}
    </div>
  );
};
