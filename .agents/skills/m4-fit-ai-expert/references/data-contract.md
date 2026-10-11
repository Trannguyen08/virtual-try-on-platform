# REFERENCE: DATA CONTRACT & SCHEMAS

## 1. Hợp đồng Dữ liệu Tổng thể (Master JSON Contract)
Dữ liệu phản hồi cuối cùng trả về cho Backend (M3) và Frontend Web (M5) phải tuân thủ nghiêm ngặt cấu trúc JSON sau:

```json
{
  "body": {
    "body_id": "b_001",
    "gender": "male",
    "measurements": {
      "height": 172.0,
      "shoulder": 44.0,
      "chest": 92.0,
      "waist": 78.0,
      "hip": 94.0
    },
    "mesh_url": "/files/b_001/body.glb"
  },
  "garment": {
    "garment_id": "tshirt_demo",
    "type": "T-Shirt",
    "brand": "Demo Brand"
  },
  "sizes": [
    { "size": "S", "score": 71.0 },
    { "size": "M", "score": 94.0 },
    { "size": "L", "score": 78.0 },
    { "size": "XL", "score": 60.0 }
  ],
  "recommended": {
    "size": "M",
    "confidence": 0.91
  },
  "fit": {
    "size": "M",
    "geometry": {
      "penetration": 95.0,
      "distance": 88.0,
      "coverage": 92.0,
      "overall": 92.0
    },
    "ai": {
      "fit_score": 91.0,
      "classification": "good_fit"
    },
    "regions": {
      "chest": "good",
      "waist": "good",
      "shoulder": "tight",
      "hip": "good"
    },
    "garment_mesh_url": "/files/b_001/tshirt_demo_M.glb",
    "heatmap_url": "/files/b_001/tshirt_demo_M_heatmap.json"
  }
}
```

---

## 2. Hợp đồng File Heatmap (`heatmap.json`)
File `heatmap.json` chứa dữ liệu khoảng cách trên từng đỉnh để Three.js tô màu chuyển sắc (vertex colors):

```json
{
  "garment_id": "tshirt_demo",
  "size": "M",
  "vertex_count": 12500,
  "unit": "cm",
  "min_distance": -0.8,
  "max_distance": 4.5,
  "distances": [0.2, 0.5, 1.2, -0.4, 2.1]
}
```

---

## 3. Quy chuẩn Đơn vị & Tọa độ
- **Trong file JSON trả về API/Frontend:** Tất cả số đo và khoảng cách đều ở đơn vị **Centimet (cm)**.
- **Trong tính toán thuật toán nội bộ (`fit/`):** Tất cả tọa độ đỉnh và khoảng cách 3D đều ở đơn vị **Mét (m)**.
- **Hệ trục tọa độ:** Khớp 100% với SMPL-X và Three.js: Right-handed, Y-up, +Z forward.
