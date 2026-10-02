import { ApiResponse } from './types';
import { BodyCustomParams, BODY_PRESETS } from '../data/bodyPresets';

export interface BodyMeasurement {
  height_cm: number;
  chest_cm: number;
  waist_cm: number;
  hip_cm: number;
  shoulder_width_cm: number;
}

export interface BodyAsset {
  source: string;
  method: string;
  format: string;
  url: string;
  notes: string[];
}

export interface BodyData {
  body_id: string;
  source: string;
  method: string;
  notes: string[];
  measurements: BodyMeasurement;
  confidence: number | null;
  mesh: BodyAsset | null;
  customParams?: BodyCustomParams;
}

export interface FitResult {
  source: string;
  method: string;
  notes: string[];
  body_id: string;
  garment_id: string;
  size: string;
  recommendation: {
    source: string;
    method: string;
    size: string;
    confidence: number | null;
    notes: string[];
  };
  overall: {
    source: string;
    method: string;
    score: number | null;
    label: 'tight' | 'good' | 'loose' | 'unknown';
    confidence: number | null;
  };
  regions: {
    region: 'chest' | 'waist' | 'hip' | 'shoulder';
    score: number | null;
    label: 'tight' | 'good' | 'loose' | 'unknown';
    confidence: number | null;
  }[];
  assets: {
    body_mesh: BodyAsset | null;
    garment_mesh: BodyAsset | null;
    tryon_mesh: BodyAsset | null;
  };
}

export interface JobData {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result: FitResult | null;
  error: { code: string; message: string } | null;
}

const API_BASE = 'http://localhost:8000';

export const tryonApi = {
  /**
   * Gọi POST /api/generate trên Blender backend nếu chạy cục bộ,
   * hoặc fallback về model GLB có sẵn trong public/models/
   */
  async generateBodyWithBlender(
    params: BodyCustomParams,
    onProgress?: (msg: string) => void
  ): Promise<{ glbUrl: string; source: 'blender-engine' | 'preset-mesh' }> {
    try {
      onProgress?.('Kết nối Blender MPFB 3D Engine...');
      const heightInMeters = params.height > 10 ? params.height / 100 : params.height;

      const payload = {
        height: heightInMeters,
        weight: params.weight,
        age: params.age || 24,
        gender: params.gender || 'female',
        proportions: {
          shoulder_width: params.proportions.shoulder_width,
          waist: params.proportions.waist,
          hips: params.proportions.hips,
          chest: params.proportions.chest,
          leg_length: params.proportions.leg_length,
          arm_length: params.proportions.arm_length,
          muscle_tone: params.proportions.muscle_tone,
          belly: params.proportions.belly,
          buttocks: params.proportions.buttocks ?? 0.5,
        },
        skin: {
          tone: params.skinTone,
          color_hex: params.skinColorHex,
        },
      };

      const res = await fetch(`${API_BASE}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        const jobId = data.job_id;
        if (jobId) {
          onProgress?.('Blender đang sinh lưới mesh 3D...');
          // Poll status
          for (let i = 0; i < 30; i++) {
            await new Promise((r) => setTimeout(r, 1000));
            const statusRes = await fetch(`${API_BASE}/api/status/${jobId}`);
            if (statusRes.ok) {
              const statusData = await statusRes.json();
              if (statusData.status === 'completed') {
                const glbPath = statusData.glb_url?.startsWith('http')
                  ? statusData.glb_url
                  : `${API_BASE}${statusData.glb_url || `/output/${jobId}.glb`}`;
                return { glbUrl: glbPath, source: 'blender-engine' };
              }
              if (statusData.status === 'failed') break;
              if (statusData.progress) {
                onProgress?.(`Blender MPFB xử lý (${statusData.progress}%)...`);
              }
            }
          }
        }
      }
    } catch {
      // Backend offline: chuyển sang mesh preset
    }

    // Static preset mesh fallback
    const fallbackUrl = params.glbModelUrl || '/models/body_default.glb';
    return { glbUrl: fallbackUrl, source: 'preset-mesh' };
  },

  /**
   * Gọi POST /api/tryon/analyze hoặc dùng mock nếu backend chưa khởi động
   */
  async analyze(
    imageFile: File | Blob,
    heightCm: number,
    customParams?: BodyCustomParams
  ): Promise<BodyData> {
    try {
      const formData = new FormData();
      formData.append('image', imageFile, 'photo.jpg');
      formData.append('height_cm', heightCm.toString());

      const res = await fetch(`${API_BASE}/api/tryon/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        const json: ApiResponse<BodyData> = await res.json();
        if (json.data) {
          if (customParams) json.data.customParams = customParams;
          return json.data;
        }
      }
    } catch {
      // Backend offline: tự động dùng client-side mock
    }

    // Client mock fallback
    await new Promise((r) => setTimeout(r, 600));
    const glbUrl = customParams?.glbModelUrl || '/models/body_default.glb';

    return {
      body_id: `body_${Date.now()}`,
      source: 'mock',
      method: 'fixed_demo_measurements',
      notes: ['Client fallback mock for frontend standalone testing'],
      measurements: {
        height_cm: heightCm,
        chest_cm: Math.round(heightCm * (customParams ? 0.45 + customParams.proportions.chest * 0.2 : 0.56)),
        waist_cm: Math.round(heightCm * (customParams ? 0.38 + customParams.proportions.waist * 0.18 : 0.47)),
        hip_cm: Math.round(heightCm * (customParams ? 0.48 + customParams.proportions.hips * 0.2 : 0.58)),
        shoulder_width_cm: Math.round(heightCm * (customParams ? 0.2 + customParams.proportions.shoulder_width * 0.12 : 0.26)),
      },
      confidence: null,
      mesh: {
        source: 'mpfb_preset',
        method: 'blender_glb_export',
        format: 'glb',
        url: glbUrl,
        notes: ['Realistic 3D MPFB human body mesh'],
      },
      customParams,
    };
  },

  /**
   * Gọi POST /api/tryon/fit và polling kết quả
   */
  async fitAndPoll(
    bodyId: string,
    garmentId: string,
    size: string,
    onProgress?: (msg: string) => void
  ): Promise<FitResult> {
    try {
      const fitRes = await fetch(`${API_BASE}/api/tryon/fit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ body_id: bodyId, garment_id: garmentId, size }),
      });

      if (fitRes.ok) {
        const fitJson: ApiResponse<JobData> = await fitRes.json();
        if (fitJson.data?.job_id) {
          const jobId = fitJson.data.job_id;
          onProgress?.('Đang kết nối mô hình xử lý 3D...');

          // Poll job
          for (let i = 0; i < 20; i++) {
            await new Promise((r) => setTimeout(r, 800));
            const jobRes = await fetch(`${API_BASE}/api/jobs/${jobId}`);
            if (jobRes.ok) {
              const jobJson: ApiResponse<JobData> = await jobRes.json();
              if (jobJson.data?.status === 'completed' && jobJson.data.result) {
                return jobJson.data.result;
              }
              if (jobJson.data?.status === 'running') {
                onProgress?.('Đang mô phỏng nếp gấp vải trên vóc dáng 3D...');
              }
            }
          }
        }
      }
    } catch {
      // Backend offline: chuyển sang client-side mock
    }

    // Client mock simulation
    onProgress?.('Lập bản đồ 3D điểm khớp cơ thể...');
    await new Promise((r) => setTimeout(r, 600));
    onProgress?.('Mô phỏng động lực học trọng lực nếp vải...');
    await new Promise((r) => setTimeout(r, 700));
    onProgress?.('Đánh giá độ căng 4 phân vùng giải phẫu...');
    await new Promise((r) => setTimeout(r, 600));

    const labelMap: Record<string, 'tight' | 'good' | 'loose'> = {
      XS: 'tight',
      S: 'tight',
      M: 'good',
      L: 'loose',
      XL: 'loose',
      XXL: 'loose',
    };
    const currentLabel = labelMap[size] || 'good';

    return {
      source: 'mock',
      method: 'fixed_demo_fit',
      notes: ['Client-side simulated fit results for development testing'],
      body_id: bodyId,
      garment_id: garmentId,
      size: size,
      recommendation: {
        source: 'mock',
        method: 'fixed_demo_recommendation',
        size: 'M',
        confidence: null,
        notes: ['Size M mang lại độ vừa vặn tối ưu cho phom người của bạn'],
      },
      overall: {
        source: 'mock',
        method: 'fixed_demo_fit',
        score: currentLabel === 'good' ? 95 : currentLabel === 'tight' ? 68 : 74,
        label: currentLabel,
        confidence: null,
      },
      regions: [
        { region: 'chest', score: currentLabel === 'good' ? 96 : 70, label: currentLabel, confidence: null },
        { region: 'waist', score: currentLabel === 'good' ? 94 : 65, label: currentLabel, confidence: null },
        { region: 'hip', score: currentLabel === 'good' ? 98 : 75, label: currentLabel, confidence: null },
        { region: 'shoulder', score: currentLabel === 'good' ? 95 : 72, label: currentLabel, confidence: null },
      ],
      assets: {
        body_mesh: {
          source: 'mock',
          method: 'box_geometry_fixture',
          format: 'glb',
          url: `${API_BASE}/api/assets/mock-body.glb`,
          notes: ['Synthetic boxes'],
        },
        garment_mesh: {
          source: 'mock',
          method: 'box_geometry_fixture',
          format: 'glb',
          url: `${API_BASE}/api/assets/mock-tshirt.glb`,
          notes: ['Synthetic boxes'],
        },
        tryon_mesh: {
          source: 'mock',
          method: 'box_geometry_fixture',
          format: 'glb',
          url: `${API_BASE}/api/assets/mock-tryon.glb`,
          notes: ['Synthetic boxes scene'],
        },
      },
    };
  },
};
