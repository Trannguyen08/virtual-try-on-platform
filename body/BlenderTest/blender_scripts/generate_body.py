"""
Blender Script: generate_body.py
Chạy TRONG Blender headless để tạo 3D body model với MPFB.

Cách chạy:
  blender --background --python generate_body.py -- --job-id <id> --output <path.glb> --params '{...}'

Yêu cầu:
  - Blender 4.x với MPFB2 addon đã cài
  - HOẶC: dùng MakeHuman data files
"""

import sys
import json
import argparse
import os
from pathlib import Path

# ─── Parse arguments từ command line ────────────────────────────────────────
def parse_args():
    """Parse arguments sau dấu '--' trong blender command."""
    # Blender truyền args sau '--'
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="Generate body với MPFB")
    parser.add_argument("--job-id", required=True, help="Job ID")
    parser.add_argument("--output", required=True, help="Output GLB path")
    parser.add_argument("--params", required=True, help="Body params JSON")
    return parser.parse_args(argv)


def main():
    args = parse_args()
    params = json.loads(args.params)
    output_path = args.output
    job_id = args.job_id

    print(f"[MPFB] Job: {job_id}")
    print(f"[MPFB] Params: {json.dumps(params, indent=2)}")
    print(f"[MPFB] Output: {output_path}")

    try:
        import bpy
    except ImportError:
        print("[ERROR] Script này phải chạy trong Blender, không phải Python thường!")
        sys.exit(1)

    # ─── Xóa scene mặc định ─────────────────────────────────────────────────
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # ─── Kiểm tra MPFB addon ─────────────────────────────────────────────────
    mpfb_module_name = None
    try:
        import bl_ext.user_default.mpfb
        mpfb_module_name = "bl_ext.user_default.mpfb"
    except ImportError:
        try:
            import mpfb
            mpfb_module_name = "mpfb"
        except ImportError:
            pass

    if mpfb_module_name:
        generate_with_mpfb(params, output_path, mpfb_module_name)
    else:
        print("[WARN] MPFB không có sẵn, dùng fallback: tạo mesh đơn giản từ params")
        generate_fallback_body(params, output_path)


def generate_with_mpfb(params: dict, output_path: str, mpfb_module_name: str = "mpfb"):
    """
    Tạo body dùng MPFB2 API.
    Tham khảo: https://static.makehumancommunity.org/mpfb.html
    """
    import bpy
    import importlib

    gender = params.get("gender", "female")
    height = params.get("height", 1.70)
    proportions = params.get("proportions", {})
    skin = params.get("skin", {})

    print(f"[MPFB] Tạo human: gender={gender}, height={height}")

    # Import MPFB module (tùy phiên bản MPFB)
    try:
        humanservice = importlib.import_module(f"{mpfb_module_name}.services.humanservice")
        modifierservice = importlib.import_module(f"{mpfb_module_name}.services.modifierservice")
        targetservice = importlib.import_module(f"{mpfb_module_name}.services.targetservice")
        HumanService = humanservice.HumanService
        ModifierService = modifierservice.ModifierService
        TargetService = targetservice.TargetService

        # Tạo human mới
        human_obj = HumanService.create_human()
        bpy.context.view_layer.objects.active = human_obj
        human_obj.select_set(True)

        # ─── Apply gender ────────────────────────────────────────────────────
        human_obj.MPFB_HUM_gender = 0.0 if gender == "female" else 1.0

        # ─── Apply age ───────────────────────────────────────────────────────
        age_normalized = (params.get("age", 25) - 10) / 70.0  # normalize 10-80 → 0-1
        human_obj.MPFB_HUM_age = age_normalized

        # ─── Apply weight/muscle ─────────────────────────────────────────────
        weight = params.get("weight", 65)
        # normalize weight (approx 40kg -> 0.0, 100kg -> 1.0)
        weight_norm = max(0.0, min(1.0, (weight - 40) / 60.0))
        human_obj.MPFB_HUM_weight = weight_norm

        muscle = proportions.get("muscle_tone", 0.5)
        human_obj.MPFB_HUM_muscle = muscle
        
        # ─── Apply custom body proportions ──────────────────────────────────
        morph_map = {
            "shoulder_width": "measure-shoulder-dist",
            "waist":          "measure-waist-circ",
            "hips":           "measure-hips-circ",
            "chest":          "measure-bust-circ",
            "belly":          "stomach-pregnant",
        }
        target_list = []
        for prop_key, target_base in morph_map.items():
            value = proportions.get(prop_key, 0.5)
            if value > 0.5:
                target_list.append({"target": f"{target_base}-incr", "value": (value - 0.5) * 2})
            elif value < 0.5:
                target_list.append({"target": f"{target_base}-decr", "value": (0.5 - value) * 2})

        if target_list:
            try:
                TargetService.bulk_load_targets(human_obj, target_list)
            except Exception as e:
                print(f"[WARN] Lỗi khi load custom targets: {e}")

        # ─── Reapply macros to update shape keys ──────────────────────────────
        TargetService.reapply_macro_details(human_obj)

        # Bake shape keys thành mesh cố định trước khi export
        TargetService.bake_targets(human_obj)

        # ─── Apply height scale ──────────────────────────────────────────────
        # MPFB human mặc định ~1.7m, scale theo chiều cao mong muốn
        default_height = 1.70
        scale_factor = height / default_height
        human_obj.scale = (scale_factor, scale_factor, scale_factor)
        bpy.ops.object.transform_apply(scale=True)

        # ─── Apply material (skin tone) ──────────────────────────────────────────
        color_hex = skin.get("color_hex", "#C68642")
        skin_color = hex_to_rgb(color_hex)

        skin_mat = bpy.data.materials.new(name="Skin")
        skin_mat.use_nodes = True
        bsdf = skin_mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*skin_color, 1.0)
            if "Subsurface Weight" in bsdf.inputs:
                bsdf.inputs["Subsurface Weight"].default_value = 0.3

        if human_obj.data.materials:
            human_obj.data.materials[0] = skin_mat
        else:
            human_obj.data.materials.append(skin_mat)

        print("[MPFB] Body created successfully")

    except ImportError as e:
        print(f"[ERROR] Lỗi import MPFB: {e}")
        print("[FALLBACK] Dùng mesh đơn giản")
        generate_fallback_body({}, output_path)
        return

    # ─── Export GLB ──────────────────────────────────────────────────────────
    export_glb(output_path)


def generate_fallback_body(params: dict, output_path: str):
    """
    Fallback: Tạo mannequin body đơn giản bằng mesh primitives.
    Dùng khi MPFB không có sẵn hoặc đang test.
    """
    import bpy
    import math

    proportions = params.get("proportions", {})
    gender = params.get("gender", "female")
    height = params.get("height", 1.70)

    # Tính toán tỉ lệ từ params
    shoulder_scale = 0.8 + proportions.get("shoulder_width", 0.5) * 0.4  # 0.8 - 1.2
    hip_scale = 0.8 + proportions.get("hips", 0.5) * 0.4
    waist_scale = 0.6 + proportions.get("waist", 0.5) * 0.3
    height_scale = height / 1.70

    # ─── Tạo body (torso) ───────────────────────────────────────────────────
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.25, location=(0, 0, height_scale * 1.45))
    head = bpy.context.active_object
    head.name = "Head"

    # Torso
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.5, location=(0, 0, height_scale * 1.05))
    torso = bpy.context.active_object
    torso.name = "Torso"
    torso.scale.x = shoulder_scale
    torso.scale.y = 0.7

    # Waist
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.2, location=(0, 0, height_scale * 0.82))
    waist = bpy.context.active_object
    waist.name = "Waist"
    waist.scale.x = waist_scale
    waist.scale.y = 0.6

    # Hips
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.3, location=(0, 0, height_scale * 0.65))
    hips = bpy.context.active_object
    hips.name = "Hips"
    hips.scale.x = hip_scale
    hips.scale.y = 0.8

    # ─── Chân ───────────────────────────────────────────────────────────────
    leg_length = 0.4 + proportions.get("leg_length", 0.5) * 0.2

    for side, x in [("L", -0.12), ("R", 0.12)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=leg_length, location=(x * shoulder_scale, 0, height_scale * 0.38))
        leg_upper = bpy.context.active_object
        leg_upper.name = f"Leg_Upper_{side}"

        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=leg_length, location=(x * shoulder_scale, 0, height_scale * 0.05))
        leg_lower = bpy.context.active_object
        leg_lower.name = f"Leg_Lower_{side}"

    # ─── Tay ─────────────────────────────────────────────────────────────────
    arm_length = 0.35 + proportions.get("arm_length", 0.5) * 0.15

    for side, x in [("L", -1), ("R", 1)]:
        x_offset = x * (0.25 * shoulder_scale)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.04, depth=arm_length,
            location=(x_offset, 0, height_scale * 1.0)
        )
        arm = bpy.context.active_object
        arm.name = f"Arm_Upper_{side}"
        arm.rotation_euler.z = math.radians(90)

    # ─── Apply material (skin tone) ──────────────────────────────────────────
    skin = params.get("skin", {})
    color_hex = skin.get("color_hex", "#C68642")
    skin_color = hex_to_rgb(color_hex)

    skin_mat = bpy.data.materials.new(name="Skin")
    skin_mat.use_nodes = True
    bsdf = skin_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*skin_color, 1.0)
    bsdf.inputs["Subsurface Weight"].default_value = 0.3

    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if obj.data.materials:
                obj.data.materials[0] = skin_mat
            else:
                obj.data.materials.append(skin_mat)

    # ─── Join tất cả objects thành 1 mesh ───────────────────────────────────
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = bpy.data.objects["Torso"]
    bpy.ops.object.join()

    print(f"[FALLBACK] Mannequin body created")
    export_glb(output_path)


def export_glb(output_path: str):
    """Export scene thành GLB file."""
    import bpy

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_apply=True,           # Apply modifiers
        export_texcoords=True,
        export_normals=True,
        export_materials='EXPORT',
        export_yup=True,             # Three.js dùng Y-up
    )
    print(f"[EXPORT] GLB saved: {output_path}")


def hex_to_rgb(hex_color: str):
    """Convert #RRGGBB sang (R, G, B) float 0-1."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))


if __name__ == "__main__":
    main()
