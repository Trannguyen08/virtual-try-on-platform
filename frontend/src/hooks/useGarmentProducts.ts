import { useEffect, useState } from 'react';
import { bodyBuilderApi } from '../api/bodyBuilderApi';
import { MOCK_PRODUCTS, Product } from '../data/mockProducts';

const labels: Record<Product['category'], string> = {
  t_shirt: 'Áo thun', shirt: 'Áo sơ mi', dress: 'Váy đầm', jacket: 'Áo khoác', pants: 'Quần',
};

export function useGarmentProducts() {
  const [products, setProducts] = useState<Product[]>(MOCK_PRODUCTS);
  const [refitStatus, setRefitStatus] = useState('Đang kiểm tra kho quần áo MPFB…');

  useEffect(() => {
    let cancelled = false;
    bodyBuilderApi.garments().then((entries) => {
      if (cancelled) return;
      const ready: Product[] = entries.filter((item) => item.available).map((item): Product => ({
        id: item.id, name: item.name, category: item.category,
        categoryLabel: labels[item.category], tagline: item.mode === 'reference_alignment'
          ? 'Căn theo chiều cao • giữ tư thế gốc' : 'Refit theo body • ảnh biểu tượng',
        price: 0, material: 'Chất liệu gốc của asset',
        imageUrl: item.category === 'pants' ? '/images/mpfb-pants.svg' : '/images/mpfb-tshirt.svg',
        gender: item.gender || 'unisex', sizes: item.sizes,
        colors: [{ name: 'Chất liệu gốc', hex: '#ffffff' }],
        fittingMode: item.mode, isNew: true,
      }));
      const ids = new Set(ready.map((item) => item.id));
      setProducts([...ready, ...MOCK_PRODUCTS.filter((item) => !ids.has(item.id))]);
      const missing = entries.length - ready.length;
      setRefitStatus(missing > 0
        ? `Kho MPFB: ${ready.length} mẫu sẵn sàng, ${missing} mẫu chưa đủ asset.`
        : `Kho MPFB: ${ready.length} mẫu sẵn sàng. Refit chưa đánh giá độ vừa theo size.`);
    }).catch(() => {
      if (!cancelled) setRefitStatus('Không tải được kho MPFB. Kiểm tra backend; các mẫu minh họa vẫn được hiển thị.');
    });
    return () => { cancelled = true; };
  }, []);

  return { products, refitStatus };
}
