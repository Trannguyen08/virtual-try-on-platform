export interface Product {
  id: string;
  name: string;
  category: 't_shirt' | 'shirt' | 'dress' | 'jacket' | 'pants';
  categoryLabel: string;
  tagline: string;
  price: number;
  originalPrice?: number;
  material: string;
  imageUrl: string;
  gender: 'womenswear' | 'menswear' | 'unisex';
  sizes: ('XS' | 'S' | 'M' | 'L' | 'XL' | 'XXL')[];
  colors: { name: string; hex: string }[];
  isHot?: boolean;
  isNew?: boolean;
  tryCount?: number;
  fittingMode?: 'body_refit' | 'reference_alignment';
  author?: string;
  license?: string;
  sourceUrl?: string;
  collection?: string;
}

/** Retained for legacy imports; products now come exclusively from the API. */
export const MOCK_PRODUCTS: Product[] = [];
