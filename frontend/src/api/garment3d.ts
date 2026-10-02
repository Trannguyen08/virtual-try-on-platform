import { API_BASE_URL } from './config';

export type GarmentView = 'front' | 'left' | 'back' | 'right';
export type GarmentImageSet = Partial<Record<GarmentView, File>> & { front: File };

export interface Garment3DError {
  code: string;
  message: string;
  retryable: boolean;
}

export interface CreateGenerationResponse {
  job_id: string;
  generation_id: string;
  input_mode: 'single_view' | 'multi_view';
  received_views: GarmentView[];
  status: string;
  poll_url: string;
}

export interface Garment3DJob {
  id: string;
  generation_id: string;
  status: string;
  progress: number;
  provider: string;
  result_url: string | null;
  error: Garment3DError | null;
  warnings: string[];
}

export interface Garment3DGeneration {
  id: string;
  status: string;
  input_mode: 'single_view' | 'multi_view';
  views: GarmentView[];
  assets: {
    glb_url: string;
    thumbnail_url: string | null;
  } | null;
  mesh: Record<string, unknown> | null;
  warnings: string[];
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.ok) return response.json() as Promise<T>;
  const body = await response.json().catch(() => ({}));
  const detail = body.detail ?? body;
  throw new Error(detail.message ?? `Request failed (${response.status})`);
}

export async function createGarmentGeneration(
  images: GarmentImageSet,
  signal?: AbortSignal,
): Promise<CreateGenerationResponse> {
  const form = new FormData();
  (['front', 'left', 'back', 'right'] as GarmentView[]).forEach((view) => {
    const file = images[view];
    if (file) form.append(view, file);
  });
  const response = await fetch(`${API_BASE_URL}/garment3d/generations`, {
    method: 'POST',
    body: form,
    signal,
  });
  return parseResponse<CreateGenerationResponse>(response);
}

export async function getGarmentJob(jobId: string, signal?: AbortSignal): Promise<Garment3DJob> {
  const response = await fetch(`${API_BASE_URL}/garment3d/jobs/${encodeURIComponent(jobId)}`, { signal });
  return parseResponse<Garment3DJob>(response);
}

export async function getGarmentGeneration(
  generationId: string,
  signal?: AbortSignal,
): Promise<Garment3DGeneration> {
  const response = await fetch(
    `${API_BASE_URL}/garment3d/generations/${encodeURIComponent(generationId)}`,
    { signal },
  );
  const generation = await parseResponse<Garment3DGeneration>(response);
  if (generation.assets) {
    generation.assets.glb_url = new URL(generation.assets.glb_url, API_BASE_URL).toString();
    if (generation.assets.thumbnail_url) {
      generation.assets.thumbnail_url = new URL(
        generation.assets.thumbnail_url,
        API_BASE_URL,
      ).toString();
    }
  }
  return generation;
}
