import { GarmentType } from '../api/garment3d';

export type SizeRegion = 'asia' | 'europe';
export type GarmentSize = 'S' | 'M' | 'L' | 'XL' | 'XXL';

export interface GarmentSizeProfile {
  widthCm: number;
  lengthCm: number;
  measurements: Array<{ label: string; valueCm: number }>;
}

const SIZES: GarmentSize[] = ['S', 'M', 'L', 'XL', 'XXL'];

// Generic display profiles only; apparel labels and garment measurements vary by brand.

type DimensionSeries = {
  label: string;
  start: number;
  step: number;
};

type GarmentChartDefinition = {
  widthDimension: number;
  lengthDimension: number;
  dimensions: DimensionSeries[];
};

type RegionCharts = Record<Exclude<GarmentType, 'auto'>, GarmentChartDefinition>;

const CHARTS: Record<SizeRegion, RegionCharts> = {
  asia: {
    tshirt: {
      widthDimension: 0,
      lengthDimension: 1,
      dimensions: [
        { label: 'Ngang ngực (đo phẳng)', start: 48, step: 2 },
        { label: 'Dài áo', start: 64, step: 2 },
        { label: 'Rộng vai', start: 40, step: 2 },
        { label: 'Dài tay', start: 19, step: 1 },
      ],
    },
    shirt: {
      widthDimension: 0,
      lengthDimension: 1,
      dimensions: [
        { label: 'Ngang ngực (đo phẳng)', start: 49, step: 2 },
        { label: 'Dài áo', start: 68, step: 2 },
        { label: 'Rộng vai', start: 41, step: 2 },
        { label: 'Dài tay', start: 59, step: 1 },
      ],
    },
    jacket: {
      widthDimension: 0,
      lengthDimension: 1,
      dimensions: [
        { label: 'Ngang ngực (đo phẳng)', start: 52, step: 2 },
        { label: 'Dài áo', start: 66, step: 2 },
        { label: 'Rộng vai', start: 43, step: 2 },
        { label: 'Dài tay', start: 60, step: 1 },
      ],
    },
    pants: {
      widthDimension: 1,
      lengthDimension: 2,
      dimensions: [
        { label: 'Ngang eo (đo phẳng)', start: 36, step: 2 },
        { label: 'Ngang mông (đo phẳng)', start: 48, step: 2 },
        { label: 'Dài quần ngoài', start: 98, step: 2 },
        { label: 'Dài ống trong', start: 72, step: 1 },
        { label: 'Ngang đùi', start: 30, step: 1 },
      ],
    },
    skirt: {
      widthDimension: 1,
      lengthDimension: 2,
      dimensions: [
        { label: 'Ngang eo (đo phẳng)', start: 34, step: 2 },
        { label: 'Ngang mông (đo phẳng)', start: 47, step: 2 },
        { label: 'Dài váy', start: 60, step: 2 },
        { label: 'Ngang gấu', start: 52, step: 2 },
      ],
    },
    dress: {
      widthDimension: 0,
      lengthDimension: 3,
      dimensions: [
        { label: 'Ngang ngực (đo phẳng)', start: 45, step: 2 },
        { label: 'Ngang eo (đo phẳng)', start: 37, step: 2 },
        { label: 'Ngang mông (đo phẳng)', start: 49, step: 2 },
        { label: 'Dài váy liền', start: 92, step: 2 },
      ],
    },
  },
  europe: {
    tshirt: {
      widthDimension: 0,
      lengthDimension: 1,
      dimensions: [
        { label: 'Ngang ngực (đo phẳng)', start: 51, step: 3 },
        { label: 'Dài áo', start: 66, step: 2 },
        { label: 'Rộng vai', start: 42, step: 2 },
        { label: 'Dài tay', start: 21, step: 1 },
      ],
    },
    shirt: {
      widthDimension: 0,
      lengthDimension: 1,
      dimensions: [
        { label: 'Ngang ngực (đo phẳng)', start: 52, step: 3 },
        { label: 'Dài áo', start: 70, step: 2 },
        { label: 'Rộng vai', start: 43, step: 2 },
        { label: 'Dài tay', start: 61, step: 1 },
      ],
    },
    jacket: {
      widthDimension: 0,
      lengthDimension: 1,
      dimensions: [
        { label: 'Ngang ngực (đo phẳng)', start: 55, step: 3 },
        { label: 'Dài áo', start: 68, step: 2 },
        { label: 'Rộng vai', start: 45, step: 2 },
        { label: 'Dài tay', start: 62, step: 1 },
      ],
    },
    pants: {
      widthDimension: 1,
      lengthDimension: 2,
      dimensions: [
        { label: 'Ngang eo (đo phẳng)', start: 38, step: 2.5 },
        { label: 'Ngang mông (đo phẳng)', start: 51, step: 2.5 },
        { label: 'Dài quần ngoài', start: 102, step: 2 },
        { label: 'Dài ống trong', start: 76, step: 1 },
        { label: 'Ngang đùi', start: 32, step: 1 },
      ],
    },
    skirt: {
      widthDimension: 1,
      lengthDimension: 2,
      dimensions: [
        { label: 'Ngang eo (đo phẳng)', start: 36, step: 2.5 },
        { label: 'Ngang mông (đo phẳng)', start: 50, step: 2.5 },
        { label: 'Dài váy', start: 62, step: 2 },
        { label: 'Ngang gấu', start: 55, step: 2 },
      ],
    },
    dress: {
      widthDimension: 0,
      lengthDimension: 3,
      dimensions: [
        { label: 'Ngang ngực (đo phẳng)', start: 48, step: 3 },
        { label: 'Ngang eo (đo phẳng)', start: 40, step: 2.5 },
        { label: 'Ngang mông (đo phẳng)', start: 52, step: 3 },
        { label: 'Dài váy liền', start: 96, step: 2 },
      ],
    },
  },
};

export function getGarmentSizeProfile(
  garmentType: GarmentType,
  region: SizeRegion,
): Record<GarmentSize, GarmentSizeProfile> | null {
  const chart = garmentType === 'auto' ? null : CHARTS[region][garmentType];
  if (!chart) return null;
  return Object.fromEntries(
    SIZES.map((size, sizeIndex) => {
      const measurements = chart.dimensions.map((dimension) => ({
        label: dimension.label,
        valueCm: Number((dimension.start + dimension.step * sizeIndex).toFixed(1)),
      }));
      return [size, {
        widthCm: measurements[chart.widthDimension].valueCm,
        lengthCm: measurements[chart.lengthDimension].valueCm,
        measurements,
      }];
    }),
  ) as Record<GarmentSize, GarmentSizeProfile>;
}
