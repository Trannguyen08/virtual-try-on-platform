import { API_BASE_URL } from './config';
import { ApiResponse } from './types';

export interface BodyParameters {
  height_cm: number;
  weight_kg: number;
  age: number;
  gender: 'female' | 'neutral' | 'male';
  skin_color: string;
  measurements_cm: {
    shoulder_width_cm: number;
    chest_cm: number;
    waist_cm: number;
    hip_cm: number;
    inseam_cm: number;
  };
  proportions: {
    shoulder_width: number;
    waist: number;
    hips: number;
    chest: number;
    leg_length: number;
    arm_length: number;
    muscle_tone: number;
    belly: number;
    buttocks: number;
  };
}

export const defaultBodyParameters = (heightCm = 170): BodyParameters => ({
  height_cm: heightCm,
  weight_kg: 65,
  age: 25,
  gender: 'neutral',
  skin_color: '#b8b8b8',
  measurements_cm: {
    shoulder_width_cm: 42, chest_cm: 90, waist_cm: 76,
    hip_cm: 95, inseam_cm: 80,
  },
  proportions: {
    shoulder_width: 0.5, waist: 0.5, hips: 0.5, chest: 0.5,
    leg_length: 0.5, arm_length: 0.5, muscle_tone: 0.5,
    belly: 0.5, buttocks: 0.5,
  },
});

export interface BodyBuilderJob {
  job_id: string;
  body_id?: string | null;
  action: 'body' | 'body_update' | 'clothing';
  status: 'pending' | 'running' | 'completed' | 'failed';
  source_id: string | null;
  asset_url: string | null;
  error: string | null;
  method: string | null;
  source: 'mock' | 'module' | 'mixed';
  parameters?: BodyParameters | null;
}

export interface RefitGarment {
  id: string;
  name: string;
  category: ProductCategory;
  gender?: 'menswear' | 'womenswear' | 'unisex';
  sizes: ('XS' | 'S' | 'M' | 'L' | 'XL' | 'XXL')[];
  available: boolean;
  error_code: string | null;
  mode: 'body_refit' | 'reference_alignment';
  thumbnail_url?: string;
  author?: string;
  license?: string;
  source?: string;
  collection?: string;
  assets?: string[];
}

type ProductCategory = 't_shirt' | 'shirt' | 'dress' | 'jacket' | 'pants';

async function request<T>(
  path: string,
  body?: object,
  signalOrMethod?: AbortSignal | 'POST' | 'PUT',
  method?: 'POST' | 'PUT',
): Promise<T> {
  const signal = typeof signalOrMethod === 'string' ? undefined : signalOrMethod;
  const requestMethod = typeof signalOrMethod === 'string'
    ? signalOrMethod
    : method || (body ? 'POST' : 'GET');
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: requestMethod,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
    signal,
  });
  const payload: ApiResponse<T> = await response.json();
  if (!response.ok || !payload.data) {
    throw new Error(payload.error?.message || `Yêu cầu thất bại (${response.status})`);
  }
  return payload.data;
}

async function waitForJob(jobId: string, signal?: AbortSignal): Promise<BodyBuilderJob> {
  for (let attempt = 0; attempt < 120; attempt += 1) {
    await new Promise((resolve) => window.setTimeout(resolve, 2000));
    signal?.throwIfAborted();
    const job = await request<BodyBuilderJob>(`/api/body-builder/jobs/${jobId}`, undefined, signal);
    if (job.status === 'completed') return job;
    if (job.status === 'failed') throw new Error(job.error || 'Blender không thể tạo mô hình');
  }
  throw new Error('Hết thời gian chờ Blender. Vui lòng thử lại.');
}

export const bodyBuilderApi = {
  garments: () => request<RefitGarment[]>('/api/body-builder/garments'),
  assetUrl: (job: BodyBuilderJob) => job.asset_url ? new URL(job.asset_url, API_BASE_URL).href : '',
  getBody: (bodyId: string) => request<BodyBuilderJob>(`/api/body-builder/bodies/${encodeURIComponent(bodyId)}`),
  async generate(parameters: BodyParameters, signal?: AbortSignal): Promise<BodyBuilderJob> {
    const job = await request<BodyBuilderJob>('/api/body-builder/generate', parameters, signal);
    return waitForJob(job.job_id, signal);
  },
  async updateBody(bodyId: string, parameters: BodyParameters): Promise<BodyBuilderJob> {
    const job = await request<BodyBuilderJob>(
      `/api/body-builder/bodies/${encodeURIComponent(bodyId)}`, parameters, 'PUT',
    );
    return waitForJob(job.job_id);
  },
  async clothing(bodyJobId: string, garmentId: string, category: string, colorHex: string, size: string, signal?: AbortSignal): Promise<BodyBuilderJob> {
    const job = await request<BodyBuilderJob>('/api/body-builder/clothing', {
      body_job_id: bodyJobId, garment_id: garmentId, category, color_hex: colorHex, size,
    }, signal);
    return waitForJob(job.job_id, signal);
  },
};
