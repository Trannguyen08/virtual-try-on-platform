# REFERENCE: HEATMAP COLORMAP & VERTEX COLOR SHADER (M5)

Đặc tả thang màu Heatmap và kỹ thuật tô màu từng đỉnh (Vertex Colors) trên mesh áo cho Module M5.

---

## 1. Thang Màu Heatmap Tiêu chuẩn

Mỗi đỉnh của mesh áo mang một giá trị khoảng cách $d$ (tính bằng mét) đo tới bề mặt da:

| Khoảng cách thực tế | Trạng thái Fit | Mã Màu Hex | Giá trị RGB $[0.0 - 1.0]$ |
| :--- | :--- | :---: | :---: |
| $d < 0.005\text{ m}$ ($< 5\text{ mm}$ hoặc xuyên thấu) | **CHẬT / CĂNG (Tight)** | `#EF4444` | $(0.94, 0.27, 0.27)$ |
| $0.005\text{ m} \le d \le 0.035\text{ m}$ | **VỪA VẶN (Good)** | `#22C55E` | $(0.13, 0.77, 0.37)$ |
| $d > 0.035\text{ m}$ ($> 3.5\text{ cm}$) | **RỘNG / THỤNG (Loose)** | `#3B82F6` | $(0.23, 0.51, 0.96)$ |

---

## 2. Kỹ thuật Áp dụng Vertex Colors trên BufferGeometry

```javascript
function applyHeatmapToGarment(mesh, distanceArray) {
  const geometry = mesh.geometry;
  const numVertices = geometry.attributes.position.count;
  const colors = new Float32Array(numVertices * 3);

  for (let i = 0; i < numVertices; i++) {
    const d = distanceArray[i] || 0.02; // mét
    let r, g, b;

    if (d < 0.005) {
      // Chật: Đỏ
      [r, g, b] = [0.94, 0.27, 0.27];
    } else if (d <= 0.035) {
      // Vừa: Xanh lá
      [r, g, b] = [0.13, 0.77, 0.37];
    } else {
      // Rộng: Xanh dương
      [r, g, b] = [0.23, 0.51, 0.96];
    }

    colors[i * 3] = r;
    colors[i * 3 + 1] = g;
    colors[i * 3 + 2] = b;
  }

  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  mesh.material.vertexColors = true;
  mesh.material.needsUpdate = true;
}
```
