"""Kịch bản Chạy Thử Thực Tế: Đánh giá Độ Vừa Vặn 3D & Xuất Heatmap JSON (Module M4).

Minh họa toàn diện luồng hoạt động kết hợp:
1. Hình học 3D Mesh (Geometry Fit Evaluator) với chẩn đoán chi tiết chật/rộng trên từng vùng.
2. Mô hình AI đã huấn luyện (SizeRecommender & FitPredictor Random Forest v1).
3. Bảng đối chiếu thông số kích thước cơ thể vs trang phục (Specs Comparison & Size Chart).

Xuất file thực tế vào thư mục `data/outputs/` để kiểm tra JSON Contract.
"""

import sys
from pathlib import Path

# Đảm bảo Python nhận diện thư mục gốc của dự án khi chạy script trực tiếp
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import numpy as np
import trimesh

from fit.evaluator import GeometryFitEvaluator
from fit.heatmap.heatmap_exporter import export_heatmap_json


def create_realistic_human_torso(height: float = 0.75, num_rings: int = 30, sections: int = 36) -> trimesh.Trimesh:
    """Tạo Mesh mô phỏng thân người (Torso Avatar) theo tỷ lệ nhân trắc học thực tế.

    Mặt cắt elip biến thiên theo chiều cao Y:
    - Vai (Y cao): Rộng 40 cm, dày 20 cm
    - Ngực: Rộng 34 cm, dày 24 cm
    - Eo (Y giữa): Rộng 28 cm, dày 20 cm
    - Hông (Y thấp): Rộng 36 cm, dày 26 cm
    """
    y_coords = np.linspace(-height / 2.0, height / 2.0, num_rings)
    angles = np.linspace(0.0, 2.0 * np.pi, sections, endpoint=False)

    vertices = []
    for y in y_coords:
        rel_y = (y + height / 2.0) / height
        if rel_y >= 0.80:  # Vai
            rx = 0.20
            rz = 0.11
        elif rel_y >= 0.60:  # Ngực
            rx = 0.17
            rz = 0.12
        elif rel_y >= 0.40:  # Eo
            rx = 0.14
            rz = 0.10
        else:  # Hông
            rx = 0.18
            rz = 0.13

        for theta in angles:
            x = rx * np.cos(theta)
            z = rz * np.sin(theta)
            vertices.append([x, y, z])

    faces = []
    for r in range(num_rings - 1):
        for s in range(sections):
            s_next = (s + 1) % sections
            v0 = r * sections + s
            v1 = r * sections + s_next
            v2 = (r + 1) * sections + s
            v3 = (r + 1) * sections + s_next
            faces.append([v0, v2, v1])
            faces.append([v1, v2, v3])

    mesh = trimesh.Trimesh(
        vertices=np.array(vertices, dtype=np.float64),
        faces=np.array(faces, dtype=np.int64),
        process=True,
    )
    return mesh


def create_garment_mesh_for_torso(
    torso_mesh: trimesh.Trimesh,
    radial_offset_cm: float,
    height_scale: float = 1.0,
) -> trimesh.Trimesh:
    """Tạo Mesh áo bao quanh thân người với khoảng cách bù (offset) xác định."""
    offset_m = radial_offset_cm / 100.0
    garment = torso_mesh.copy()
    normals = garment.vertex_normals
    garment.vertices += normals * offset_m

    if height_scale < 1.0:
        garment.vertices[:, 1] *= height_scale

    return garment


def run_demo():
    print("=" * 85)
    print("  VIRTUAL TRY-ON PLATFORM - DEMO ĐÁNH GIÁ ĐỘ VỪA VẶN 3D & DỰ ĐOÁN AI (MODULE M4)")
    print("=" * 85)

    # 1. Khởi tạo avatar cơ thể người thực tế
    print("\n[1/5] Khởi tạo mô hình 3D Torso Avatar (chuẩn nhân trắc học)...")
    torso = create_realistic_human_torso(height=0.75, num_rings=30, sections=36)

    # Số đo cơ thể chuẩn của người dùng giả lập
    user_measurements = {
        "bust": 92.0,      # Vòng ngực: 92 cm
        "waist": 74.0,     # Vòng eo: 74 cm
        "hip": 96.0,       # Vòng hông: 96 cm
        "shoulder": 42.0,  # Chiều rộng vai: 42 cm
        "height": 170.0,   # Chiều cao: 170 cm
    }

    print(f"      -> Tổng số đỉnh cơ thể (Body Vertices): {len(torso.vertices):,} đỉnh")
    print(f"      -> Tổng số mặt tam giác (Body Faces):  {len(torso.faces):,} tam giác")
    print("      -> Số đo cơ thể người dùng:")
    print(f"         Ngực: {user_measurements['bust']} cm | Eo: {user_measurements['waist']} cm | "
          f"Hông: {user_measurements['hip']} cm | Vai: {user_measurements['shoulder']} cm | Cao: {user_measurements['height']} cm")

    # 2. Định nghĩa 3 kích cỡ áo thử nghiệm kèm THÔNG SỐ SẢN PHẨM THỰC TẾ
    test_cases = [
        {
            "size": "S",
            "name": "Áo Size S (Chật / Too Tight)",
            "offset_cm": -0.8,
            "garment_id": "cotton_tshirt_v1_S",
            "garment_specs": {"bust": 90.0, "length": 68.0, "shoulder": 41.0, "waist": 82.0},
        },
        {
            "size": "M",
            "name": "Áo Size M (Vừa vặn / Good Fit)",
            "offset_cm": 2.2,
            "garment_id": "cotton_tshirt_v1_M",
            "garment_specs": {"bust": 98.0, "length": 70.0, "shoulder": 44.0, "waist": 90.0},
        },
        {
            "size": "XL",
            "name": "Áo Size XL (Rộng thùng thình / Too Loose)",
            "offset_cm": 5.2,
            "garment_id": "cotton_tshirt_v1_XL",
            "garment_specs": {"bust": 114.0, "length": 74.0, "shoulder": 50.0, "waist": 106.0},
        },
    ]

    output_dir = Path("data/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []

    print("\n[2/5] Đánh giá tích hợp (Hình học 3D + AI + Bảng thông số kỹ thuật sản phẩm)...")
    print("-" * 88)

    for tc in test_cases:
        size = tc["size"]
        g_specs = tc["garment_specs"]
        garment = create_garment_mesh_for_torso(torso, radial_offset_cm=tc["offset_cm"])

        evaluator = GeometryFitEvaluator(garment_id=tc["garment_id"], size=size)
        res = evaluator.evaluate(
            body_mesh=torso,
            garment_mesh=garment,
            body_measurements=user_measurements,
            garment_specs=g_specs,
        )
        results.append((tc, res, garment))

        # Xuất file Heatmap JSON thực tế
        out_path = output_dir / f"demo_heatmap_size_{size.lower()}.json"
        export_heatmap_json(res["heatmap"], output_path=out_path)

        bust_ease = g_specs["bust"] - user_measurements["bust"]

        print(f"\n>>> THỬ ĐỒ VỚI: {tc['name'].upper()}")
        print(f"    * Thông số áo Size {size} : Ngực={g_specs['bust']:.1f} cm | Dài={g_specs['length']:.1f} cm | Vai={g_specs['shoulder']:.1f} cm | Eo={g_specs['waist']:.1f} cm")
        print(f"    * Độ chênh ngực (Ease): {bust_ease:+.1f} cm (Ngực áo {g_specs['bust']:.1f} cm vs Ngực người {user_measurements['bust']:.1f} cm)")
        print(f"    * Fit Score 3D Mesh : {res['fit_score']:.1f} / 100 điểm")
        print(f"    * Phân loại 3D Mesh : {res['classification']}")
        print(f"    * Khoảng cách TB    : {res['metrics']['avg_distance_cm']:.2f} cm")
        print(f"    * Tỷ lệ xuyên thấu  : {res['metrics']['penetration_ratio'] * 100:.1f}% "
              f"(Độ lẹm sâu nhất: {res['metrics']['max_penetration_depth_cm']:.2f} cm)")

        # In chẩn đoán chi tiết chật / rộng
        diag = res["diagnostics"]
        print(f"    * Lời khuyên hình học : {diag['summary_advice']}")
        print("    * Chẩn đoán chi tiết từng vùng giải phẫu:")
        for reg_k, reg_v in diag["region_details"].items():
            icon = "❌" if reg_v["status"] == "TIGHT" else ("⚠️" if reg_v["status"] == "LOOSE" else "✅")
            print(f"        {icon} [{reg_v['name_vi']:<4}]: {reg_v['advice']}")

        # In phân tích từ Mô hình AI
        ai_in = res["ai_insights"]
        rec = ai_in["recommended_size_specs"]
        print(f"    * Kết quả Mô hình AI:")
        print(f"        -> AI đánh giá Size {size} đang thử : {ai_in['ai_predicted_fit_class']} (Score dự đoán: {ai_in['ai_predicted_fit_score']:.1f} điểm)")
        print(f"        -> AI ĐỀ XUẤT SIZE TỐI ƯU   : Size {rec['size']} (Độ tin cậy: {rec['confidence']*100:.0f}%)")
        print(f"        -> Thông số của size đề xuất: Ngực {rec['specs_cm']['garment_bust']} cm | Dài {rec['specs_cm']['garment_length']} cm | Vai {rec['specs_cm']['garment_shoulder']} cm")
        print(f"        -> Lý do đề xuất            : {rec['why_recommended']}")
        print(f"        -> Mức độ đồng thuận AI vs 3D: {'ĐỒNG THUẬN HOÀN TOÀN ✅' if ai_in['ai_vs_geometry_agreement'] else 'CÓ ĐỘ LỆCH VỀ FORM DÁNG ℹ️'}")

        print(f"    -> Đã xuất file Heatmap JSON: {out_path}")

    # 3. Bảng tổng hợp đối chứng 3 kích cỡ
    print("\n" + "=" * 88)
    print("  [3/5] BẢNG TỔNG HỢP ĐỐI CHỨNG CẢ 3 SIZE THỬ ĐỒ TRÊN AVATAR 3D")
    print("=" * 88)
    header = f"{'Kích cỡ':<8} | {'Ngực áo':<10} | {'Độ chênh (Ease)':<16} | {'Khoảng cách TB':<15} | {'3D Fit Score':<13} | {'Phân loại':<12} | {'Khuyến nghị':<15}"
    print(header)
    print("-" * len(header))
    for tc, res, _ in results:
        g_b = tc["garment_specs"]["bust"]
        ease = g_b - user_measurements["bust"]
        rec = "Nên tăng size" if res["classification"] == "Too Tight" else ("Hoàn hảo" if res["classification"] == "Good" else "Nên giảm size")
        row = (
            f"Size {tc['size']:<3} | "
            f"{g_b:>5.1f} cm   | "
            f"{ease:>+5.1f} cm        | "
            f"{res['metrics']['avg_distance_cm']:>5.2f} cm        | "
            f"{res['fit_score']:>5.1f} / 100    | "
            f"{res['classification']:<12} | "
            f"{rec:<15}"
        )
        print(row)

    # 4. Bảng đối chiếu thông số số đo minh bạch cho người dùng (Specs Comparison)
    print("\n" + "=" * 88)
    print("  [4/5] BẢNG THÔNG SỐ SẢN PHẨM & ĐỐI CHIẾU SỐ ĐO NGƯỜI DÙNG (SIZE CHART MATRIX)")
    print("=" * 88)
    specs = results[1][1]["specs_comparison"]
    print(f"Số đo người dùng: Ngực {specs['user_measurements_cm']['bust']}cm | Eo {specs['user_measurements_cm']['waist']}cm | Vai {specs['user_measurements_cm']['shoulder']}cm | Cao {specs['user_measurements_cm']['height']}cm\n")

    matrix_header = f"{'Size':<12} | {'Ngực áo':<10} | {'Dài áo':<9} | {'Vai áo':<9} | {'Độ chênh ngực':<16} | {'Form dáng':<24} | {'Đánh giá'}"
    print(matrix_header)
    print("-" * len(matrix_header))
    for item in specs["size_chart_matrix"]:
        curr_tag = " [Đang thử]" if item["is_current_trial"] else ""
        rec_tag = "⭐ KHUYÊN DÙNG" if item["is_recommended"] else ("Vừa người" if item["bust_ease_cm"] > 0 else "Chật ngực (không vừa)")
        row = (
            f"{item['size'] + curr_tag:<12} | "
            f"{item['garment_bust_cm']:>5.1f} cm   | "
            f"{item['garment_length_cm']:>5.1f} cm | "
            f"{item['garment_shoulder_cm']:>5.1f} cm | "
            f"{item['bust_ease_cm']:>+5.1f} cm         | "
            f"{item['fit_style']:<24} | "
            f"{rec_tag}"
        )
        print(row)

    print(f"\n-> HƯỚNG DẪN DÀNH CHO NGƯỜI DÙNG: {specs['user_guide']}")

    # 5. Xem mẫu JSON thực tế gửi cho Frontend Three.js
    sample_json_path = output_dir / "demo_heatmap_size_m.json"
    with open(sample_json_path, "r", encoding="utf-8") as f:
        sample_data = json.load(f)

    print("\n" + "=" * 88)
    print(f"  [5/5] CẤU TRÚC JSON OUTPUT THỰC TẾ TRUYỀN SANG FRONTEND THREE.JS (M5)")
    print("=" * 88)
    sample_res = results[1][1]
    ui_contract_preview = {
        "fit_score": sample_res["fit_score"],
        "classification": sample_res["classification"],
        "ai_recommendation": sample_res["ai_insights"]["recommended_size_specs"],
        "diagnostics": {
            "summary_advice": sample_res["diagnostics"]["summary_advice"],
            "tight_regions": sample_res["diagnostics"]["tight_regions"],
            "good_regions": sample_res["diagnostics"]["good_regions"],
            "loose_regions": sample_res["diagnostics"]["loose_regions"],
        },
        "heatmap_3d": {
            "garment_id": sample_data["garment_id"],
            "size": sample_data["size"],
            "unit": sample_data["unit"],
            "total_vertices": sample_data["vertex_count"],
            "first_5_distances_cm": sample_data["distances"][:5],
        },
    }
    print(json.dumps(ui_contract_preview, indent=4, ensure_ascii=False))
    print("\n" + "=" * 88)
    print("  -> HOÀN TẤT DEMO: Dữ liệu đã lưu tại data/outputs/demo_heatmap_size_*.json")
    print("=" * 88)


if __name__ == "__main__":
    run_demo()
