export interface BodyProportions {
  shoulder_width: number; // 0.0 - 1.0
  waist: number;          // 0.0 - 1.0
  hips: number;           // 0.0 - 1.0
  chest: number;          // 0.0 - 1.0
  belly: number;          // 0.0 - 1.0
  muscle_tone: number;    // 0.0 - 1.0
  leg_length: number;     // 0.0 - 1.0
  arm_length: number;     // 0.0 - 1.0
  buttocks?: number;      // 0.0 - 1.0
}

export interface BodyCustomParams {
  height: number;
  weight: number;
  gender: 'female' | 'male';
  age: number;
  proportions: BodyProportions;
  skinTone: 'light' | 'medium' | 'dark';
  skinColorHex: string;
  selectedPresetId?: string;
  glbModelUrl: string;
}

export interface BodyPreset {
  id: string;
  name: string;
  gender: 'female' | 'male';
  height: number;
  weight: number;
  stats: string;
  description: string;
  img: string;
  glbModelUrl: string;
  proportions: BodyProportions;
}

export const BODY_PRESETS: BodyPreset[] = [
  {
    id: 'slim',
    name: 'Linh Đan (Slim Fit)',
    gender: 'female',
    height: 170,
    weight: 50,
    stats: '1m70 • 50kg',
    description: 'Vóc dáng thanh mảnh, tỷ lệ eo thon và vai gọn.',
    img: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500&auto=format&fit=crop&q=80',
    glbModelUrl: '/models/body_default.glb',
    proportions: {
      shoulder_width: 0.35,
      waist: 0.28,
      hips: 0.35,
      chest: 0.35,
      belly: 0.05,
      muscle_tone: 0.2,
      leg_length: 0.6,
      arm_length: 0.5,
      buttocks: 0.4,
    },
  },
  {
    id: 'athletic',
    name: 'Minh Quân (Athletic)',
    gender: 'male',
    height: 180,
    weight: 74,
    stats: '1m80 • 74kg',
    description: 'Khung vai chữ V, cơ bắp săn chắc và tỷ lệ chuẩn thể thao.',
    img: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500&auto=format&fit=crop&q=80',
    glbModelUrl: '/models/body_athletic.glb',
    proportions: {
      shoulder_width: 0.8,
      waist: 0.42,
      hips: 0.5,
      chest: 0.75,
      belly: 0.1,
      muscle_tone: 0.85,
      leg_length: 0.65,
      arm_length: 0.65,
      buttocks: 0.55,
    },
  },
  {
    id: 'curvy',
    name: 'Thanh Trúc (Curvy Hourglass)',
    gender: 'female',
    height: 165,
    weight: 68,
    stats: '1m65 • 68kg',
    description: 'Đường cong đồng hồ cát quyến rũ, vòng hông và ngực nở nang.',
    img: 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=500&auto=format&fit=crop&q=80',
    glbModelUrl: '/models/body_curvy.glb',
    proportions: {
      shoulder_width: 0.52,
      waist: 0.45,
      hips: 0.85,
      chest: 0.78,
      belly: 0.3,
      muscle_tone: 0.25,
      leg_length: 0.48,
      arm_length: 0.48,
      buttocks: 0.8,
    },
  },
  {
    id: 'petite',
    name: 'Mai Anh (Petite)',
    gender: 'female',
    height: 158,
    weight: 46,
    stats: '1m58 • 46kg',
    description: 'Vóc dáng nhỏ nhắn, cân đối đặc trưng của phụ nữ Á Đông.',
    img: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=500&auto=format&fit=crop&q=80',
    glbModelUrl: '/models/body_female_mpfb.glb',
    proportions: {
      shoulder_width: 0.3,
      waist: 0.3,
      hips: 0.4,
      chest: 0.38,
      belly: 0.12,
      muscle_tone: 0.15,
      leg_length: 0.4,
      arm_length: 0.4,
      buttocks: 0.42,
    },
  },
];
