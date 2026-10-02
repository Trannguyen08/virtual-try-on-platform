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
}

export const MOCK_PRODUCTS: Product[] = [
  {
    id: 'demo-tshirt',
    name: 'Áo thun Minimalist Signature',
    category: 't_shirt',
    categoryLabel: 'Áo thun',
    tagline: 'Streetwear Luxe',
    price: 299000,
    originalPrice: 350000,
    material: 'Cotton 100%',
    imageUrl: 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop&q=80',
    gender: 'unisex',
    sizes: ['S', 'M', 'L', 'XL'],
    colors: [
      { name: 'Đen Obsidian', hex: '#0a050d' },
      { name: 'Trắng Chalk', hex: '#f5f5f5' },
      { name: 'Xanh Midnight Navy', hex: '#03035e' },
    ],
    isHot: true,
    isNew: true,
    tryCount: 1420,
  },
  {
    id: 'silk-classic-shirt',
    name: 'Áo sơ mi Silk Blend Classic',
    category: 'shirt',
    categoryLabel: 'Áo sơ mi',
    tagline: 'Office Chic',
    price: 399000,
    originalPrice: 480000,
    material: 'Lụa Tơ Tằm',
    imageUrl: 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800&auto=format&fit=crop&q=80',
    gender: 'womenswear',
    sizes: ['XS', 'S', 'M', 'L'],
    colors: [
      { name: 'Trắng Chalk', hex: '#f5f5f5' },
      { name: 'Be Silk', hex: '#f3ebd8' },
      { name: 'Hồng Pastel', hex: '#f9d5e5' },
    ],
    isHot: true,
    tryCount: 980,
  },
  {
    id: 'midi-pleated-dress',
    name: 'Váy Midi Pleated Haute',
    category: 'dress',
    categoryLabel: 'Váy đầm',
    tagline: 'Parisian Elegance',
    price: 549000,
    originalPrice: 650000,
    material: 'Chiffon Lụa',
    imageUrl: 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800&auto=format&fit=crop&q=80',
    gender: 'womenswear',
    sizes: ['XS', 'S', 'M'],
    colors: [
      { name: 'Đen Obsidian', hex: '#0a050d' },
      { name: 'Xanh Midnight Navy', hex: '#03035e' },
    ],
    isNew: true,
    tryCount: 750,
  },
  {
    id: 'tailored-blazer-jacket',
    name: 'Blazer Tailored Structured',
    category: 'jacket',
    categoryLabel: 'Áo khoác',
    tagline: 'Modern Power',
    price: 699000,
    originalPrice: 850000,
    material: 'Dạ Wool Pha',
    imageUrl: 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&auto=format&fit=crop&q=80',
    gender: 'unisex',
    sizes: ['S', 'M', 'L', 'XL'],
    colors: [
      { name: 'Đen Obsidian', hex: '#0a050d' },
      { name: 'Xanh Olive', hex: '#4b5320' },
      { name: 'Be Silk', hex: '#f3ebd8' },
    ],
    isHot: true,
    tryCount: 1650,
  },
  {
    id: 'linen-oversized-shirt',
    name: 'Áo Sơ Mi Linen Casual Relax',
    category: 'shirt',
    categoryLabel: 'Áo sơ mi',
    tagline: 'Summer Breeze',
    price: 349000,
    material: '100% French Linen',
    imageUrl: 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=800&auto=format&fit=crop&q=80',
    gender: 'menswear',
    sizes: ['M', 'L', 'XL'],
    colors: [
      { name: 'Trắng Chalk', hex: '#f5f5f5' },
      { name: 'Xanh Olive', hex: '#4b5320' },
    ],
    tryCount: 520,
  },
  {
    id: 'graphic-vintage-tshirt',
    name: 'Áo thun Heavyweight Vintage Boxy',
    category: 't_shirt',
    categoryLabel: 'Áo thun',
    tagline: 'Underground Tone',
    price: 279000,
    material: 'Cotton 280gsm',
    imageUrl: 'https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=800&auto=format&fit=crop&q=80',
    gender: 'unisex',
    sizes: ['S', 'M', 'L', 'XL', 'XXL'],
    colors: [
      { name: 'Đen Obsidian', hex: '#0a050d' },
      { name: 'Xanh Midnight Navy', hex: '#03035e' },
    ],
    tryCount: 890,
  },
  {
    id: 'evening-silk-slip-dress',
    name: 'Đầm Lụa Slip Dress Dạ Hội',
    category: 'dress',
    categoryLabel: 'Váy đầm',
    tagline: 'Night Gala',
    price: 599000,
    material: 'Satin Silk Cao Cấp',
    imageUrl: 'https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=800&auto=format&fit=crop&q=80',
    gender: 'womenswear',
    sizes: ['XS', 'S', 'M'],
    colors: [
      { name: 'Đen Obsidian', hex: '#0a050d' },
      { name: 'Hồng Pastel', hex: '#f9d5e5' },
    ],
    isNew: true,
    tryCount: 610,
  },
  {
    id: 'denim-jacket-utility',
    name: 'Áo Khoác Denim Utility Oversize',
    category: 'jacket',
    categoryLabel: 'Áo khoác',
    tagline: 'Rugged Streetwear',
    price: 520000,
    material: 'Denim Cotton 13oz',
    imageUrl: 'https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=800&auto=format&fit=crop&q=80',
    gender: 'unisex',
    sizes: ['S', 'M', 'L', 'XL'],
    colors: [
      { name: 'Xanh Midnight Navy', hex: '#03035e' },
      { name: 'Đen Obsidian', hex: '#0a050d' },
    ],
    tryCount: 1140,
  },
];
