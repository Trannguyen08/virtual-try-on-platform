import { GarmentLandmark } from '../api/garment3d';
import { GarmentType } from '../api/garment3d';

export interface GarmentViewerAnnotation {
  id: string;
  label: string;
  bodyRegion: string;
  frontPosition: [number, number, number];
  backPosition: [number, number, number];
  estimated: boolean;
}

type AnnotationDefinition = {
  landmark: string;
  label: string;
  bodyRegion: string;
  estimated?: boolean;
};

const UPPER_BODY_POINTS: AnnotationDefinition[] = [
  { landmark: 'neck_center', label: 'Cổ', bodyRegion: 'Cổ áo' },
  { landmark: 'left_shoulder', label: 'Vai trái', bodyRegion: 'Vai trái' },
  { landmark: 'right_shoulder', label: 'Vai phải', bodyRegion: 'Vai phải' },
  { landmark: 'left_armpit', label: 'Ngực trái', bodyRegion: 'Ngực' },
  { landmark: 'right_armpit', label: 'Ngực phải', bodyRegion: 'Ngực' },
  { landmark: 'waist_left', label: 'Bụng/eo trái', bodyRegion: 'Bụng và eo' },
  { landmark: 'waist_right', label: 'Bụng/eo phải', bodyRegion: 'Bụng và eo' },
];

const BOTTOM_POINTS: AnnotationDefinition[] = [
  { landmark: 'waist_left', label: 'Eo trái', bodyRegion: 'Eo' },
  { landmark: 'waist_right', label: 'Eo phải', bodyRegion: 'Eo' },
  { landmark: 'hip_left', label: 'Hông trái', bodyRegion: 'Hông' },
  { landmark: 'hip_right', label: 'Hông phải', bodyRegion: 'Hông' },
  { landmark: 'crotch_center', label: 'Đũng quần', bodyRegion: 'Đũng' },
  { landmark: 'left_hem', label: 'Gấu trái', bodyRegion: 'Ống chân/gấu' },
  { landmark: 'right_hem', label: 'Gấu phải', bodyRegion: 'Ống chân/gấu' },
  { landmark: 'hem_left', label: 'Gấu trái', bodyRegion: 'Chân' },
  { landmark: 'hem_right', label: 'Gấu phải', bodyRegion: 'Chân' },
];

function asPosition(value: unknown): [number, number, number] | null {
  if (
    !Array.isArray(value) ||
    value.length !== 3 ||
    !value.every((coordinate) => typeof coordinate === 'number' && Number.isFinite(coordinate))
  ) {
    return null;
  }
  return [value[0], value[1], value[2]];
}

function getPoints(landmarks: Record<string, GarmentLandmark>, definitions: AnnotationDefinition[]) {
  return definitions.flatMap((definition) => {
    const landmark = landmarks[definition.landmark];
    if (landmark?.annotation_visible === false) return [];
    const frontPosition = asPosition(landmark?.front_position_m);
    const backPosition = asPosition(landmark?.back_position_m);
    if (!frontPosition || !backPosition) return [];
    return [{
      id: definition.landmark,
      label: definition.label,
      bodyRegion: definition.bodyRegion,
      frontPosition,
      backPosition,
      estimated: definition.estimated ?? false,
    }];
  });
}

export function buildGarmentAnnotations(
  garmentType: GarmentType,
  landmarks?: Record<string, GarmentLandmark>,
): GarmentViewerAnnotation[] {
  if (!landmarks) return [];

  if (garmentType === 'pants' || garmentType === 'skirt') {
    return getPoints(landmarks, BOTTOM_POINTS);
  }

  // Only show landmarks returned by the image analysis. Do not invent arm or
  // elbow locations by interpolating along a sleeve, since short sleeves do
  // not contain enough visual evidence for those body parts.
  return getPoints(landmarks, UPPER_BODY_POINTS);
}
