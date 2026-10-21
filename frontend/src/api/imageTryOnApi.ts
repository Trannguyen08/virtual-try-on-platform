import { API_BASE_URL } from './config';
import { GarmentType } from './garment3d';

export type TryOnGarmentType = Exclude<GarmentType, 'auto'>;

export interface OutfitGarmentUpload {
  slot: 'upper' | 'lower' | 'onepiece';
  garment_type: TryOnGarmentType;
  reference_value_cm: number;
  fit_mode: 'auto' | 'measurements';
  ease_cm: number;
  garment_measurements_cm?: {
    chest_circumference_cm?: number;
    waist_circumference_cm?: number;
    hip_circumference_cm?: number;
    hem_circumference_cm?: number;
  };
  front: File;
  back?: File;
}
import { ApiResponse } from './types';

export interface ImageTryOnResult {
  source: 'module' | 'mixed' | 'mock';
  method: string;
  notes: string[];
  body_id: string;
  garment_type: string;
  garments: Array<{
    slot: 'upper' | 'lower' | 'onepiece';
    garment_type: TryOnGarmentType;
    reconstruction: Record<string, unknown>;
  }>;
  tryon_mesh: {
    source: string;
    method: string;
    notes: string[];
    format: 'glb';
    url: string;
  };
  simulation_ran: boolean;
  penetration_fraction: number;
  placement: string;
  warnings: string[];
  reconstruction: {
    garments?: Array<Record<string, unknown>>;
    mode?: string;
    segmentation?: Record<string, unknown>;
    scale?: Record<string, unknown>;
    mesh?: Record<string, unknown>;
  };
}

export interface ImageTryOnJob {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  attempt_count: number;
  request: {
    body_id: string;
    garments: Array<{
      slot: 'upper' | 'lower' | 'onepiece';
      garment_type: TryOnGarmentType;
      reference_measurement: 'garment_length';
      reference_value_cm: number;
      fit_mode: 'auto' | 'measurements';
      ease_cm: number;
      garment_measurements_cm?: OutfitGarmentUpload['garment_measurements_cm'];
    }>;
    simulate_cloth: boolean;
  };
  result: ImageTryOnResult | null;
  error: { code: string; message: string } | null;
}

async function parseJob(response: Response): Promise<ImageTryOnJob> {
  const payload: ApiResponse<ImageTryOnJob> = await response.json();
  if (!response.ok || !payload.data) {
    throw new Error(payload.error?.message || `Yêu cầu thất bại (${response.status})`);
  }
  return payload.data;
}

export const imageTryOnApi = {
  assetUrl: (url: string) => new URL(url, API_BASE_URL).href,
  async create(bodyId: string, garments: OutfitGarmentUpload[], signal?: AbortSignal): Promise<ImageTryOnJob> {
    const form = new FormData();
    form.append('body_id', bodyId);
    form.append('garments_json', JSON.stringify(garments.map((item) => ({
      slot: item.slot,
      garment_type: item.garment_type,
      reference_value_cm: item.reference_value_cm,
      fit_mode: item.fit_mode,
      ease_cm: item.ease_cm,
      garment_measurements_cm: item.garment_measurements_cm,
    }))));
    garments.forEach((item, index) => {
      form.append(`garment_${index}_front`, item.front);
      if (item.back) form.append(`garment_${index}_back`, item.back);
    });
    return parseJob(await fetch(`${API_BASE_URL}/api/tryon/image-jobs`, {
      method: 'POST', body: form, signal,
    }));
  },
  async get(jobId: string, signal?: AbortSignal): Promise<ImageTryOnJob> {
    return parseJob(await fetch(
      `${API_BASE_URL}/api/tryon/image-jobs/${encodeURIComponent(jobId)}`,
      { signal },
    ));
  },
};
