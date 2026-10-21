/**
 * API Client kết nối Module M4 (AI & Fit Recommendation) cho Frontend.
 * 
 * Cung cấp:
 * 1. recommendSize(): Gợi ý size tối ưu từ vóc dáng người dùng và bảng size shop.
 * 2. askStylistChat(): Trợ lý ảo Stylist tư vấn may đo (có Guardrail chống spam).
 * 3. evaluateFit(): Đánh giá chi tiết điểm Fit Score và phân lớp chật/vừa/rộng từng vùng.
 * 4. checkAiHealth(): Kiểm tra trạng thái sẵn sàng của AI services.
 */

import { API_BASE_URL } from './config';

// =============================================================================
// TYPES & INTERFACES
// =============================================================================
export interface SizeChart {
  [sizeName: string]: {
    bust?: number;
    waist?: number;
    hip?: number;
    length?: number;
    shoulder?: number;
    [key: string]: number | undefined;
  };
}

export interface SizeRecommendationPayload {
  height_cm: number;
  weight_kg: number;
  gender?: string;
  garment_category?: string;
  fit_preference?: string;
  size_chart: SizeChart;
  body_measurements?: {
    bust?: number;
    waist?: number;
    hip?: number;
    shoulder?: number;
  };
}

export interface SizeRecommendationResult {
  status: string;
  recommendation: {
    recommended_size: string;
    confidence: number;
    actual_bust_ease_cm: number;
    reason: string;
  };
  estimated_body_measurements: Record<string, number>;
  target_dimensions: Record<string, number>;
  all_candidates: Record<
    string,
    {
      score: number;
      actual_bust_ease_cm?: number;
      fit_status?: string;
      [key: string]: any;
    }
  >;
}

export interface ChatStylistPayload {
  query: string;
  height_cm?: number;
  weight_kg?: number;
  gender?: string;
  garment_category?: string;
  fit_preference?: string;
  size_chart?: SizeChart;
  body_measurements?: Record<string, number>;
  current_trial_specs?: Record<string, any>;
  fit_diagnostics?: Record<string, any>;
}

export interface ChatStylistResult {
  status: string;
  reply: string;
  source: string;
  is_refusal: boolean;
}

export interface FitEvaluationPayload {
  body_measurements: Record<string, number>;
  garment_specs: Record<string, number>;
  garment_category?: string;
}

export interface FitEvaluationResult {
  status: string;
  fit_score: number;
  fit_class: 'Good' | 'Too Tight' | 'Too Loose';
  region_evaluations: Record<string, string>;
  diagnostics?: Record<string, any>;
}

export interface AiHealthResult {
  status: string;
  module: string;
  guardrail_active: boolean;
  cache_capacity: number;
  advisor_ready: boolean;
  version: string;
}

// =============================================================================
// API FUNCTIONS
// =============================================================================

/**
 * Gửi yêu cầu gợi ý size thông minh theo vóc dáng và bảng size.
 */
export async function recommendSize(
  payload: SizeRecommendationPayload
): Promise<SizeRecommendationResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/ai/recommend-size`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Lỗi gợi ý size (${response.status})`);
  }

  return response.json();
}

/**
 * Gửi tin nhắn hỏi đáp tư vấn với AI Stylist.
 */
export async function askStylistChat(
  payload: ChatStylistPayload
): Promise<ChatStylistResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/ai/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Lỗi kết nối Stylist (${response.status})`);
  }

  return response.json();
}

/**
 * Đánh giá độ vừa vặn và phân vùng chật/rộng giữa số đo cơ thể và trang phục.
 */
export async function evaluateFit(
  payload: FitEvaluationPayload
): Promise<FitEvaluationResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/ai/evaluate-fit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Lỗi đánh giá độ vừa (${response.status})`);
  }

  return response.json();
}

/**
 * Kiểm tra trạng thái sẵn sàng của AI Router.
 */
export async function checkAiHealth(): Promise<AiHealthResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/ai/health`);
  if (!response.ok) {
    throw new Error(`AI Service không phản hồi (${response.status})`);
  }
  return response.json();
}

export const aiApi = {
  recommendSize,
  askStylistChat,
  evaluateFit,
  checkAiHealth,
};

export default aiApi;
