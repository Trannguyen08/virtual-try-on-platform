"""
Script: scripts/test/test_real_garment_pipeline.py
Mục đích:
Kiểm thử thực tế quy trình nạp ảnh trang phục từ Web hoặc file cục bộ,
chuyển đổi và sinh mô hình 3D thực thụ (True 3D Manifold Mesh), kiểm định
độ sâu (Z depth > 20cm, không bị 2.5D dẹt), đối soát chu vi ngực chuẩn xác theo Size Chart.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from urllib.request import urlopen, Request

import numpy as np
from PIL import Image, ImageDraw
import trimesh

from garment.size_chart.garment_loader import GarmentLoader, SizeMeasurement
from garment.mesh.mesh_generator import GarmentMeshGenerator
from garment.mesh.size_scaling import SizeScaler
from garment.reconstruction.validation import GlbValidator


# URL ảnh áo T-Shirt thật từ Wikimedia Commons (Public Domain / CC0)
DEFAULT_WEB_IMAGE_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/"
    "Blue_Tshirt.jpg/512px-Blue_Tshirt.jpg"
)


def fetch_or_create_garment_image(image_source: str, cache_path: Path) -> Image.Image:
    """Tải ảnh từ URL trên Web hoặc đọc từ đường dẫn file cục bộ."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Nếu là đường dẫn file cục bộ tồn tại
    local_p = Path(image_source)
    if local_p.is_file():
        print(f"[*] Đọc ảnh trang phục từ file cục bộ: {local_p}")
        return Image.open(local_p).convert("RGBA")

    # 2. Nếu là URL web
    if image_source.startswith("http://") or image_source.startswith("https://"):
        print(f"[*] Đang tải ảnh trang phục từ Web: {image_source} ...")
        try:
            req = Request(image_source, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=10) as response:
                cache_path.write_bytes(response.read())
            print(f"[+] Tải ảnh thành công, lưu đệm tại: {cache_path}")
            return Image.open(cache_path).convert("RGBA")
        except Exception as e:
            print(f"[!] Không thể tải từ Web ({e}). Tự động sinh ảnh T-shirt chuẩn thực tế để test...")

    # 3. Fallback: Sinh ảnh T-shirt chi tiết có cổ áo, tay áo và hoa văn
    print("[*] Sinh ảnh T-Shirt chân thực với đường may và cổ áo...")
    w, h = 512, 512
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Thân áo xanh navy cao cấp
    navy = (28, 54, 98, 255)
    seam = (18, 38, 72, 255)
    polygon = [
        (170, 70),
        (115, 105),
        (55, 160),
        (105, 225),
        (150, 190),
        (150, 450),
        (362, 450),
        (362, 190),
        (407, 225),
        (457, 160),
        (397, 105),
        (342, 70),
        (310, 95),
        (202, 95),
    ]
    draw.polygon(polygon, fill=navy)
    # Đường viền may (seam)
    draw.line(polygon + [polygon[0]], fill=seam, width=2)
    # Cổ áo tròn (crew neck)
    draw.arc([200, 70, 312, 120], start=0, end=180, fill=(240, 240, 240, 255), width=4)

    img.save(cache_path)
    return img


def run_pipeline_test(
    image_input: str,
    output_dir: Path,
    target_size: str = "M",
) -> dict:
    """Thực thi kiểm định toàn diện quy trình sinh 3D Garment từ ảnh."""
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_img_path = output_dir / "input_garment.png"
    glb_output_path = output_dir / f"garment_3d_{target_size.lower()}.glb"
    obj_output_path = output_dir / f"garment_3d_{target_size.lower()}.obj"
    report_path = output_dir / "pipeline_report.json"

    # Bước 1: Nạp ảnh
    garment_img = fetch_or_create_garment_image(image_input, raw_img_path)

    # Bước 2: Nạp thông số Size Chart
    print(f"\n[*] Nạp bảng thông số Size Chart chuẩn (Size: {target_size})...")
    loader = GarmentLoader()
    chart = loader.load_category("tshirt")
    spec = chart.get_size(target_size)
    print(f"    - Vòng ngực chuẩn: {spec.chest_cm:.1f} cm ({spec.chest_m:.3f} m)")
    print(f"    - Chiều dài áo:    {spec.length_cm:.1f} cm ({spec.length_m:.3f} m)")
    print(f"    - Rộng vai áo:     {spec.shoulder_width_cm:.1f} cm ({spec.shoulder_width_m:.3f} m)")

    # Bước 3: Sinh mô hình 3D Manifold thực thụ với UV Texture từ ảnh
    print("\n[*] Sinh mô hình 3D Manifold Mesh (Torso elip 3D, ống tay 3D, cổ áo rỗng)...")
    generator = GarmentMeshGenerator(base_y_offset=0.90)
    mesh_3d = generator.generate_tshirt(spec, texture_image=garment_img)

    # Xuất file 3D
    generator.export_mesh(mesh_3d, glb_output_path)
    generator.export_mesh(mesh_3d, obj_output_path)
    print(f"[+] Đã xuất mô hình 3D GLB: {glb_output_path}")
    print(f"[+] Đã xuất mô hình 3D OBJ: {obj_output_path}")

    # Bước 4: Kiểm định không gian 3D (Đảm bảo KHÔNG PHẢI 2.5D dẹt)
    bounds = mesh_3d.bounds
    x_span = float(bounds[1][0] - bounds[0][0])
    y_span = float(bounds[1][1] - bounds[0][1])
    z_span = float(bounds[1][2] - bounds[0][2])
    vertex_count = len(mesh_3d.vertices)
    face_count = len(mesh_3d.faces)

    print("\n" + "=" * 60)
    print("📊 KẾT QUẢ ĐO ĐẠC KHÔNG GIAN HÌNH HỌC 3D:")
    print("=" * 60)
    print(f" - Số đỉnh (Vertices):        {vertex_count} (Quy chuẩn <= 30.000)")
    print(f" - Số mặt (Faces/Triangles):  {face_count}")
    print(f" - Chiều ngang (X span):      {x_span:.3f} m ({x_span*100:.1f} cm)")
    print(f" - Chiều cao (Y span):        {y_span:.3f} m ({y_span*100:.1f} cm)")
    print(f" - Chiều sâu thân (Z span):   {z_span:.3f} m ({z_span*100:.1f} cm)")

    # Tiêu chí Z depth: Phải >= 0.20m (20cm) để ôm vừa cơ thể người thật
    is_true_3d = z_span >= 0.20
    print(f" -> Đánh giá 3D thực thụ:     {'ĐẠT CHUẨN 3D (Z depth sâu thực tế) ✅' if is_true_3d else 'CHƯA ĐẠT (Bị dẹt 2.5D) ❌'}")

    # Bước 5: Kiểm định chu vi lát cắt (Cross-section Slicing theo TC-GAR-04)
    scaler = SizeScaler(generator=generator)
    passed_size, measured_chest_cm, delta_cm = scaler.verify_size_accuracy(
        mesh_3d, expected_chest_cm=spec.chest_cm, tolerance_cm=1.0
    )
    print("\n" + "=" * 60)
    print("📏 KIỂM ĐỊNH CHU VI LÁT CẮT (CROSS-SECTION SLICING — TC-GAR-04):")
    print("=" * 60)
    print(f" - Chu vi ngực kỳ vọng (Size {target_size}): {spec.chest_cm:.2f} cm")
    print(f" - Chu vi ngực đo trên mesh 3D:     {measured_chest_cm:.2f} cm")
    print(f" - Độ sai lệch:                      {delta_cm:.2f} cm (Cho phép <= 1.0 cm)")
    print(f" -> Kết quả nghiệm thu TC-GAR-04:    {'PASS ✅ (Sai lệch <= 1.0 cm)' if passed_size else 'FAIL ❌'}")

    # Bước 6: Kiểm định tính hợp lệ của file GLB xuất ra (GlbValidator)
    validator = GlbValidator()
    glb_meta = validator.validate(glb_output_path)
    print("\n" + "=" * 60)
    print("🔍 KIỂM ĐỊNH FILE GLB CHUẨN (GLTF 2.0 VALIDATION):")
    print("=" * 60)
    print(f" - Kích thước file:                  {glb_meta.file_size_bytes / 1024:.1f} KB")
    print(f" - Số tam giác:                      {glb_meta.triangle_count}")
    print(f" - Vật liệu PBR gán ảnh texture:     {'CÓ (PBR Material)' if glb_meta.has_pbr_material else 'KHÔNG'}")
    print(f" - Số lượng texture nhúng:           {glb_meta.texture_count}")

    report = {
        "status": "PASS" if (is_true_3d and passed_size) else "FAIL",
        "target_size": target_size,
        "vertex_count": vertex_count,
        "face_count": face_count,
        "dimensions_m": {"x": x_span, "y": y_span, "z": z_span},
        "depth_cm": z_span * 100.0,
        "is_true_3d": is_true_3d,
        "size_validation": {
            "expected_chest_cm": spec.chest_cm,
            "measured_chest_cm": measured_chest_cm,
            "delta_cm": delta_cm,
            "passed": passed_size,
        },
        "glb_metadata": {
            "file_size_bytes": glb_meta.file_size_bytes,
            "triangle_count": glb_meta.triangle_count,
            "has_pbr": glb_meta.has_pbr_material,
        },
        "output_files": {
            "glb": str(glb_output_path),
            "obj": str(obj_output_path),
        },
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n[+] Đã lưu báo cáo kiểm định: {report_path}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Kiểm thử Pipeline sinh mô hình 3D Garment thực thụ từ ảnh Web"
    )
    parser.add_argument(
        "--image",
        type=str,
        default=DEFAULT_WEB_IMAGE_URL,
        help="Đường dẫn file ảnh cục bộ hoặc URL ảnh trên web",
    )
    parser.add_argument(
        "--size",
        type=str,
        default="M",
        choices=["S", "M", "L", "XL"],
        help="Size trang phục cần sinh (S, M, L, XL)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/outputs/test_garment_3d",
        help="Thư mục xuất file mô hình 3D",
    )
    args = parser.parse_args()

    report = run_pipeline_test(
        image_input=args.image,
        output_dir=Path(args.output_dir),
        target_size=args.size,
    )

    if report["status"] == "PASS":
        print("\n🎉 TOÀN BỘ TIÊU CHÍ 3D VÀ SIZE CHUẨN ĐỀU ĐẠT TRẠNG THÁI PASS! 🎉\n")
        sys.exit(0)
    else:
        print("\n⚠️ CÓ TIÊU CHÍ CHƯA ĐẠT! VUI LÒNG KIỂM TRA LẠI LOG. ⚠️\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
