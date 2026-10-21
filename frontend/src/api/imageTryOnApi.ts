import { API_BASE_URL } from './config';
import { GarmentImageSet, GarmentType } from './garment3d';
import { ApiResponse } from './types';

export interface ImageTryOnResult {
  source: 'module' | 'mixed' | 'mock';
  method: string;
  notes: string[];
  body_id: string;
  garment_type: GarmentType;
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
    mode: string;
    segmentation: Record<string, unknown>;
    scale: Record<string, unknown>;
    mesh: Record<string, unknown>;
  };
}

export interface ImageTryOnJob {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  attempt_count: number;
  request: {
    body_id: string;
    garment_type: GarmentType;
    reference_measurement: 'garment_length';
    reference_value_cm: number;
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
  async create(bodyId: string, images: GarmentImageSet, garmentType: GarmentType,
    referenceValueCm: number, signal?: AbortSignal): Promise<ImageTryOnJob> {
    const form = new FormData();
    form.append('body_id', bodyId);
    form.append('garment_type', garmentType);
    form.append('reference_value_cm', String(referenceValueCm));
    (['front', 'left', 'back', 'right'] as const).forEach((view) => {
      const file = images[view];
      if (file) form.append(view, file);
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
