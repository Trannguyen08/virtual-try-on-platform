import React, { useState } from 'react';
import { recommendSize, SizeChart, SizeRecommendationResult } from '../../api/aiApi';
import { Product } from '../../data/mockProducts';

interface AiSizeAdvisorModalProps {
  isOpen: boolean;
  onClose: () => void;
  product: Product;
  onSelectSize: (size: string) => void;
}

export const AiSizeAdvisorModal: React.FC<AiSizeAdvisorModalProps> = ({
  isOpen,
  onClose,
  product,
  onSelectSize,
}) => {
  const [heightCm, setHeightCm] = useState<number>(170);
  const [weightKg, setWeightKg] = useState<number>(65);
  const [gender, setGender] = useState<'male' | 'female' | 'unisex'>('unisex');
  const [fitPreference, setFitPreference] = useState<'regular' | 'slim' | 'oversized'>('regular');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SizeRecommendationResult | null>(null);

  if (!isOpen) return null;

  // Xây dựng bảng size tương ứng từ các size của sản phẩm
  const buildProductSizeChart = (): SizeChart => {
    const isPants = product.category === 'pants';
    const chart: SizeChart = {};
    const sizeKeys = product.sizes.length > 0 ? product.sizes : ['S', 'M', 'L', 'XL'];

    sizeKeys.forEach((s, idx) => {
      if (isPants) {
        chart[s] = {
          waist: 72 + idx * 4,
          hip: 92 + idx * 4,
          length: 98 + idx * 2,
        };
      } else {
        // Áo thun / sơ mi / áo khoác
        chart[s] = {
          bust: 90 + idx * 8,
          length: 68 + idx * 2,
          shoulder: 41 + idx * 3,
          waist: 84 + idx * 8,
        };
      }
    });

    return chart;
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const sizeChart = buildProductSizeChart();
      const res = await recommendSize({
        height_cm: heightCm,
        weight_kg: weightKg,
        gender: gender,
        garment_category: product.category === 't_shirt' ? 'tshirt' : product.category,
        fit_preference: fitPreference,
        size_chart: sizeChart,
      });
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Không thể kết nối máy chủ phân tích kích cỡ.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(2, 6, 23, 0.75)',
        backdropFilter: 'blur(8px)',
        zIndex: 1100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem',
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: '#ffffff',
          borderRadius: '1.25rem',
          maxWidth: '560px',
          width: '100%',
          maxHeight: '90vh',
          overflowY: 'auto',
          boxShadow: '0 25px 50px -12px rgba(8, 10, 97, 0.25)',
          padding: '1.75rem',
          position: 'relative',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
            background: '#f1f5f9',
            border: 'none',
            borderRadius: '50%',
            width: '2rem',
            height: '2rem',
            cursor: 'pointer',
            fontSize: '1rem',
            color: '#64748b',
          }}
        >
          Đóng
        </button>

        {/* Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '1.25rem' }}>
          <div
            style={{
              width: '2.5rem',
              height: '2.5rem',
              borderRadius: '0.65rem',
              background: 'linear-gradient(135deg, #080a61 0%, #3d7eff 100%)',
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.25rem',
            }}
          >
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, color: '#0f172a' }}>
              Trợ lý AI Gợi ý Kích cỡ (Size Advisor)
            </h3>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#64748b' }}>
              Ứng dụng mô hình Nhân trắc học và Phân tích độ cử động vải (Ease)
            </p>
          </div>
        </div>

        {/* Input Form */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: '#334155', marginBottom: '0.35rem' }}>
              Chiều cao (cm)
            </label>
            <input
              type="number"
              min={120}
              max={220}
              value={heightCm}
              onChange={(e) => setHeightCm(Number(e.target.value))}
              style={{
                width: '100%',
                padding: '0.6rem 0.75rem',
                borderRadius: '0.5rem',
                border: '1px solid #cbd5e1',
                fontSize: '0.9rem',
                outline: 'none',
                boxSizing: 'border-box',
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: '#334155', marginBottom: '0.35rem' }}>
              Cân nặng (kg)
            </label>
            <input
              type="number"
              min={35}
              max={160}
              value={weightKg}
              onChange={(e) => setWeightKg(Number(e.target.value))}
              style={{
                width: '100%',
                padding: '0.6rem 0.75rem',
                borderRadius: '0.5rem',
                border: '1px solid #cbd5e1',
                fontSize: '0.9rem',
                outline: 'none',
                boxSizing: 'border-box',
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: '#334155', marginBottom: '0.35rem' }}>
              Giới tính
            </label>
            <select
              value={gender}
              onChange={(e) => setGender(e.target.value as any)}
              style={{
                width: '100%',
                padding: '0.6rem 0.75rem',
                borderRadius: '0.5rem',
                border: '1px solid #cbd5e1',
                fontSize: '0.9rem',
                outline: 'none',
                backgroundColor: '#fff',
                boxSizing: 'border-box',
              }}
            >
              <option value="unisex">Unisex / Trung tính</option>
              <option value="male">Nam giới</option>
              <option value="female">Nữ giới</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: '#334155', marginBottom: '0.35rem' }}>
              Gu mặc mong muốn
            </label>
            <select
              value={fitPreference}
              onChange={(e) => setFitPreference(e.target.value as any)}
              style={{
                width: '100%',
                padding: '0.6rem 0.75rem',
                borderRadius: '0.5rem',
                border: '1px solid #cbd5e1',
                fontSize: '0.9rem',
                outline: 'none',
                backgroundColor: '#fff',
                boxSizing: 'border-box',
              }}
            >
              <option value="regular">Vừa vặn (Regular Fit)</option>
              <option value="slim">Ôm sát (Slim Fit)</option>
              <option value="oversized">Rộng rãi (Oversized)</option>
            </select>
          </div>
        </div>

        {/* Action Button */}
        <button
          type="button"
          onClick={handleAnalyze}
          disabled={loading}
          style={{
            width: '100%',
            padding: '0.75rem',
            background: 'linear-gradient(135deg, #080a61 0%, #1e3a8a 50%, #3d7eff 100%)',
            color: '#fff',
            border: 'none',
            borderRadius: '0.65rem',
            fontWeight: 700,
            fontSize: '0.95rem',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1,
            marginBottom: '1rem',
            boxShadow: '0 4px 12px rgba(8, 10, 97, 0.2)',
          }}
        >
          {loading ? 'Đang phân tích số đo...' : 'Phân tích số đo và tìm size phù hợp'}
        </button>

        {error && (
          <div style={{ padding: '0.75rem', backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '0.5rem', color: '#b91c1c', fontSize: '0.82rem', marginBottom: '1rem' }}>
            {error}
          </div>
        )}

        {/* Result Card */}
        {result && (
          <div
            style={{
              padding: '1.25rem',
              backgroundColor: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '0.85rem',
              marginTop: '0.5rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#64748b', textTransform: 'uppercase' }}>
                  Kích cỡ khuyến nghị
                </span>
                <div style={{ fontSize: '1.85rem', fontWeight: 900, color: '#080a61', lineHeight: 1.1 }}>
                  Size {result.recommendation.recommended_size}
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '0.72rem', color: '#64748b' }}>Độ tin cậy</span>
                <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#10b981' }}>
                  {Math.round(result.recommendation.confidence * 100)}%
                </div>
              </div>
            </div>

            <p style={{ margin: '0 0 0.85rem', fontSize: '0.85rem', color: '#334155', lineHeight: 1.5 }}>
              {result.recommendation.reason}
            </p>

            {/* Estimated Body Profile Chips */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.45rem', marginBottom: '1rem' }}>
              <span style={{ fontSize: '0.72rem', padding: '3px 8px', backgroundColor: '#e2e8f0', borderRadius: '999px', color: '#334155' }}>
                Ngực: ~{result.estimated_body_measurements.bust || 90} cm
              </span>
              <span style={{ fontSize: '0.72rem', padding: '3px 8px', backgroundColor: '#e2e8f0', borderRadius: '999px', color: '#334155' }}>
                Eo: ~{result.estimated_body_measurements.waist || 76} cm
              </span>
              <span style={{ fontSize: '0.72rem', padding: '3px 8px', backgroundColor: '#e2e8f0', borderRadius: '999px', color: '#334155' }}>
                Vai: ~{result.estimated_body_measurements.shoulder || 42} cm
              </span>
            </div>

            <button
              type="button"
              onClick={() => {
                onSelectSize(result.recommendation.recommended_size);
                onClose();
              }}
              style={{
                width: '100%',
                padding: '0.65rem',
                backgroundColor: '#10b981',
                color: '#fff',
                border: 'none',
                borderRadius: '0.5rem',
                fontWeight: 700,
                fontSize: '0.88rem',
                cursor: 'pointer',
              }}
            >
              Áp dụng size {result.recommendation.recommended_size} cho đơn hàng
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
