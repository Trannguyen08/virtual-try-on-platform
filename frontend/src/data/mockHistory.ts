export interface TryOnHistoryRegion {
  score: number;
  label: 'good' | 'tight' | 'loose';
  text: string;
}

export interface TryOnHistoryItem {
  id: string;
  productId: string;
  productName: string;
  category: 't_shirt' | 'shirt' | 'dress' | 'jacket' | 'pants';
  categoryLabel: string;
  price: number;
  formattedPrice: string;
  size: string;
  colorName: string;
  colorHex: string;
  date: string;
  timestamp: number;
  originalPhotoUrl: string;
  resultPhotoUrl: string;
  fitScore: number;
  inCart: boolean;
  regions: {
    chest: TryOnHistoryRegion;
    waist: TryOnHistoryRegion;
    hip: TryOnHistoryRegion;
    shoulder: TryOnHistoryRegion;
  };
  notes?: string;
}

export const INITIAL_MOCK_HISTORY: TryOnHistoryItem[] = [
  {
    id: 'hist-001',
    productId: 'demo-tshirt',
    productName: 'Áo thun Minimalist Signature',
    category: 't_shirt',
    categoryLabel: 'Áo thun',
    price: 299000,
    formattedPrice: '299.000₫',
    size: 'M',
    colorName: 'Đen phối Trắng',
    colorHex: '#0a050d',
    date: '12/09/2026 • 14:32',
    timestamp: 1789223520000,
    originalPhotoUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=800&auto=format&fit=crop&q=80',
    resultPhotoUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuB4EVWrXOjEKwx7jDsWiHwRzZn-HW0SaZ18zmX9zoKI7er5r7OlPc8Sfiusja6x_xP3xIzl-vTFY2JRQCUzUhYel0JI7nP9SEXAnM_n8mxDzHdHy4wAoh3cQ1Zk5jGakfXeVf61B1BqkVfYqfLWlZiuXFhAvEOXmCAk9fslvvk9kS_UXS5oHkE1-EHVXhqCb6fqBiumIUpbBd9kkW4ouu82-LpL3AS-kTL61veNkm9U5opjTxBiBWT3Ig',
    fitScore: 99.4,
    inCart: true,
    regions: {
      chest: { score: 99, label: 'good', text: 'Chuẩn form' },
      waist: { score: 100, label: 'good', text: 'Chuẩn form' },
      hip: { score: 98, label: 'good', text: 'Chuẩn form' },
      shoulder: { score: 100, label: 'good', text: 'Khớp vai hoàn hảo' },
    },
    notes: 'Vừa vặn hoàn hảo với vòng ngực 96cm và eo 80cm.',
  },
  {
    id: 'hist-002',
    productId: 'silk-classic-shirt',
    productName: 'Áo sơ mi Silk Blend Classic',
    category: 'shirt',
    categoryLabel: 'Áo sơ mi',
    price: 399000,
    formattedPrice: '399.000₫',
    size: 'M',
    colorName: 'Be Champagne',
    colorHex: '#f3ebd8',
    date: '10/09/2026 • 09:15',
    timestamp: 1789031700000,
    originalPhotoUrl: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=800&auto=format&fit=crop&q=80',
    resultPhotoUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAGb0E-IqTewTgyZTE8xELsA9zT9BgnvOcVGlNK3BBxlv4cPC92mOaijP8Dt0TZLhmsR-eHcgj2Rx7B_JJps9R4BOGb9DOgSrw8WH8JXibcZcu8Xb7nCuCHvFG8vKfvNVgudj2o-8RCiV_2AGXTUFsTmSB_mhKI1K-fPoRKZ66F3ie3iZma4n_0biyhmL2XLoKRAxPBgMgcuQvh7KcQSHvHCKVwCsqOVwk-eyT_Sxk7xrNY1fqNQrZfbw',
    fitScore: 98.9,
    inCart: false,
    regions: {
      chest: { score: 98, label: 'good', text: 'Vừa vặn' },
      waist: { score: 99, label: 'good', text: 'Chuẩn form' },
      hip: { score: 97, label: 'good', text: 'Thoải mái' },
      shoulder: { score: 99, label: 'good', text: 'Chuẩn vai' },
    },
    notes: 'Lụa tơ tằm mềm mại rủ tự nhiên theo bờ vai.',
  },
  {
    id: 'hist-003',
    productId: 'tailored-blazer-jacket',
    productName: 'Blazer Tailored Structured AI',
    category: 'jacket',
    categoryLabel: 'Áo khoác',
    price: 699000,
    formattedPrice: '699.000₫',
    size: 'L',
    colorName: 'Xanh Midnight Navy',
    colorHex: '#03035e',
    date: '08/09/2026 • 16:45',
    timestamp: 1788885900000,
    originalPhotoUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&auto=format&fit=crop&q=80',
    resultPhotoUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBQsPccBGI2rzTGDoDBZ0MrRlclj3hQ_NmehiuY6R3dgCYF77EKqghiJR-yPS7D9HQhDwu5VO-MDHL0xN1EbScCgB-gtzOSVx5S6uPbuLrKNJtae0-hL0VE0KtPs5UUpc2GeoSlBBaK7rud9m79M_j-7qsWNJIjNbMWUcWWePgAduOm2aWckbJ4SpGq7zNi4mEFsqTKOpIrL3hQRXlV5L4jzsIDDdj9MdpFiZXQkiXZl0s7eKJ09aNvpw',
    fitScore: 99.1,
    inCart: true,
    regions: {
      chest: { score: 99, label: 'good', text: 'Chuẩn form' },
      waist: { score: 98, label: 'good', text: 'Vừa vặn' },
      hip: { score: 100, label: 'good', text: 'Chuẩn phom blazer' },
      shoulder: { score: 100, label: 'good', text: 'Đệm vai đứng dáng' },
    },
    notes: 'Đệm vai vuông vức, phần eo ôm nhẹ theo vóc dáng.',
  },
  {
    id: 'hist-004',
    productId: 'midi-pleated-dress',
    productName: 'Váy Midi Pleated Haute Couture',
    category: 'dress',
    categoryLabel: 'Váy đầm',
    price: 549000,
    formattedPrice: '549.000₫',
    size: 'S',
    colorName: 'Đen Obsidian',
    colorHex: '#0a050d',
    date: '05/09/2026 • 11:20',
    timestamp: 1788607200000,
    originalPhotoUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=800&auto=format&fit=crop&q=80',
    resultPhotoUrl: 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800&auto=format&fit=crop&q=80',
    fitScore: 97.6,
    inCart: true,
    regions: {
      chest: { score: 96, label: 'tight', text: 'Hơi ôm ngực' },
      waist: { score: 98, label: 'good', text: 'Chuẩn eo thon' },
      hip: { score: 100, label: 'good', text: 'Xếp ly xòe tự nhiên' },
      shoulder: { score: 97, label: 'good', text: 'Vừa vặn' },
    },
    notes: 'Vòng ngực hơi ôm nếu thích thoải mái hơn có thể cân nhắc size M.',
  },
  {
    id: 'hist-005',
    productId: 'wide-leg-trousers',
    productName: 'Quần Wide-Leg Trousers Haute',
    category: 'pants',
    categoryLabel: 'Quần',
    price: 459000,
    formattedPrice: '459.000₫',
    size: 'M',
    colorName: 'Ghi Khói',
    colorHex: '#565f6e',
    date: '02/09/2026 • 18:10',
    timestamp: 1788357000000,
    originalPhotoUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&auto=format&fit=crop&q=80',
    resultPhotoUrl: 'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=800&auto=format&fit=crop&q=80',
    fitScore: 98.2,
    inCart: false,
    regions: {
      chest: { score: 100, label: 'good', text: 'N/A' },
      waist: { score: 98, label: 'good', text: 'Cạp vừa vặn' },
      hip: { score: 99, label: 'good', text: 'Rộng rãi thanh lịch' },
      shoulder: { score: 100, label: 'good', text: 'N/A' },
    },
    notes: 'Chiều dài ống quần phủ vừa chạm gót giày khi mang giày 3-5cm.',
  },
];
