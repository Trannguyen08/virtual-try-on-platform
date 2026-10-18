import { API_BASE_URL } from './config';

const GARMENT3D_API_BASE_URL = API_BASE_URL;

export type GarmentView = 'front' | 'left' | 'back' | 'right';
export type GarmentImageSet = Partial<Record<GarmentView, File>> & { front: File };
export type GarmentType = 'tshirt' | 'shirt' | 'jacket' | 'pants' | 'skirt' | 'dress';

export interface GarmentGenerationOptions {
  garmentType: GarmentType;
  referenceMeasurement?: string;
  referenceValueCm?: number;
}

export interface GarmentMeasurement {
  value_cm: number | null;
  value_px: number;
  method: string;
  source: string;
  confidence: number;
}

export interface GarmentLandmark {
  image_px?: [number, number];
  image_normalized?: [number, number];
  front_vertex?: number;
  back_vertex?: number;
  front_position_m?: [number, number, number];
  back_position_m?: [number, number, number];
  source?: string;
  annotation_visible?: boolean;
}

export interface GarmentAttachmentRegion {
  body_region: string;
  landmarks: string[];
  front_vertex_indices: number[];
  recommended_clearance_cm: number;
}

export interface BodyReadyGarmentMetadata {
  schema_version: string;
  reconstruction_mode: string;
  fit_ready: boolean;
  garment_type: GarmentType;
  measurements: Record<string, GarmentMeasurement>;
  landmarks?: Record<string, GarmentLandmark>;
  attachment_regions?: Record<string, GarmentAttachmentRegion>;
  warnings: string[];
}

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
    metadata_url: string | null;
  } | null;
  mesh: Record<string, unknown> | null;
  garment: BodyReadyGarmentMetadata | null;
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
  options: GarmentGenerationOptions,
  signal?: AbortSignal,
): Promise<CreateGenerationResponse> {
  const form = new FormData();
  (['front', 'left', 'back', 'right'] as GarmentView[]).forEach((view) => {
    const file = images[view];
    if (file) form.append(view, file);
  });
  form.append('garment_type', options.garmentType);
  if (options.referenceMeasurement && options.referenceValueCm) {
    form.append('reference_measurement', options.referenceMeasurement);
    form.append('reference_value_cm', String(options.referenceValueCm));
  }
  const response = await fetch(`${GARMENT3D_API_BASE_URL}/garment3d/generations`, {
    method: 'POST',
    body: form,
    signal,
  });
  return parseResponse<CreateGenerationResponse>(response);
}

export async function getGarmentJob(jobId: string, signal?: AbortSignal): Promise<Garment3DJob> {
  const response = await fetch(`${GARMENT3D_API_BASE_URL}/garment3d/jobs/${encodeURIComponent(jobId)}`, { signal });
  return parseResponse<Garment3DJob>(response);
}

export async function getGarmentGeneration(
  generationId: string,
  signal?: AbortSignal,
): Promise<Garment3DGeneration> {
  const response = await fetch(
    `${GARMENT3D_API_BASE_URL}/garment3d/generations/${encodeURIComponent(generationId)}`,
    { signal },
  );
  const generation = await parseResponse<Garment3DGeneration>(response);
  if (generation.assets) {
    generation.assets.glb_url = new URL(generation.assets.glb_url, GARMENT3D_API_BASE_URL).toString();
    if (generation.assets.thumbnail_url) {
      generation.assets.thumbnail_url = new URL(
        generation.assets.thumbnail_url,
        GARMENT3D_API_BASE_URL,
      ).toString();
    }
    if (generation.assets.metadata_url) {
      generation.assets.metadata_url = new URL(
        generation.assets.metadata_url,
        GARMENT3D_API_BASE_URL,
      ).toString();
    }
  }
  return generation;
}
