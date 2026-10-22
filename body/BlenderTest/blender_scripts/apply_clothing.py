"""
Blender Script: apply_clothing.py
Apply clothing asset lên body model có sẵn.

Cách chạy:
  blender --background --python apply_clothing.py -- --job-id <id> --output <path.glb> --params '{...}'
"""

import sys
import json
import argparse
from pathlib import Path


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser()
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--params", required=True)
    return parser.parse_args(argv)


def main():
    args = parse_args()
    params = json.loads(args.params)
    output_path = args.output

    print(f"[CLOTHING] Job: {args.job_id}")
    print(f"[CLOTHING] Params: {json.dumps(params, indent=2)}")

    try:
        import bpy
    except ImportError:
        print("[ERROR] Phải chạy trong Blender!")
        sys.exit(1)

    # ─── Load body model từ source GLB ──────────────────────────────────────
    source_glb = params.get("source_glb")
    if not source_glb or not Path(source_glb).exists():
        print(f"[ERROR] Source GLB không tồn tại: {source_glb}")
        sys.exit(1)

    # Xóa scene mặc định
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Import body GLB
    bpy.ops.import_scene.gltf(filepath=source_glb)
    print(f"[CLOTHING] Loaded body from: {source_glb}")

    # ─── Load clothing asset ─────────────────────────────────────────────────
    clothing_id = params.get("clothing_id", "tshirt_basic")
    color_hex = params.get("color_hex", "#FFFFFF")

    # Đường dẫn clothing asset
    assets_dir = Path(__file__).parent.parent / "assets" / "clothing"
    clothing_glb = assets_dir / f"{clothing_id}.glb"
    clothing_obj_file = assets_dir / f"{clothing_id}.obj"

    if clothing_glb.exists():
        bpy.ops.import_scene.gltf(filepath=str(clothing_glb))
        print(f"[CLOTHING] Loaded: {clothing_glb}")
    elif clothing_obj_file.exists():
        bpy.ops.import_scene.obj(filepath=str(clothing_obj_file))
        print(f"[CLOTHING] Loaded: {clothing_obj_file}")
    else:
        print(f"[WARN] Clothing asset không tồn tại: {clothing_id}, tạo placeholder")
        create_placeholder_clothing(clothing_id, color_hex)

    # ─── Apply color material cho clothing ──────────────────────────────────
    apply_clothing_color(color_hex)

    # ─── Fit clothing lên body ───────────────────────────────────────────────
    # TODO: Dùng MPFB clothing fitting hoặc shrinkwrap modifier
    fit_clothing_to_body(params.get("size_override"))

    # ─── Export ─────────────────────────────────────────────────────────────
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_apply=True,
        export_materials='EXPORT',
        export_yup=True,
    )
    print(f"[CLOTHING] Exported: {output_path}")


def apply_clothing_color(color_hex: str):
    """Apply màu lên clothing object."""
    import bpy

    def hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

    color = hex_to_rgb(color_hex)

    # Tìm clothing objects (objects được import sau body)
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and "Clothing" in obj.name:
            mat = bpy.data.materials.new(name=f"Clothing_{color_hex}")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            bsdf.inputs["Base Color"].default_value = (*color, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.8

            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)


def create_placeholder_clothing(clothing_id: str, color_hex: str):
    """Tạo clothing placeholder khi không có asset thật."""
    import bpy
    import math

    def hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

    color = hex_to_rgb(color_hex)

    # Tạo mesh đơn giản dựa theo clothing_id
    if "shirt" in clothing_id or "top" in clothing_id:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.45, location=(0, 0, 1.05))
        obj = bpy.context.active_object
        obj.name = "Clothing_Shirt"
    elif "jean" in clothing_id or "pant" in clothing_id or "bottom" in clothing_id:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.20, depth=0.5, location=(0, 0, 0.55))
        obj = bpy.context.active_object
        obj.name = "Clothing_Pants"
    elif "dress" in clothing_id:
        bpy.ops.mesh.primitive_cone_add(radius1=0.35, radius2=0.15, depth=0.8, location=(0, 0, 0.75))
        obj = bpy.context.active_object
        obj.name = "Clothing_Dress"
    else:
        return

    # Apply material
    mat = bpy.data.materials.new(name="Clothing")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
    obj.data.materials.append(mat)


def fit_clothing_to_body(size_override=None):
    """
    Fit clothing lên body dùng Shrinkwrap modifier.
    Đây là placeholder - production cần MPFB clothing fitting.
    """
    import bpy

    clothing_objects = [o for o in bpy.data.objects if "Clothing" in o.name and o.type == 'MESH']
    body_objects = [o for o in bpy.data.objects if "Clothing" not in o.name and o.type == 'MESH']

    if not clothing_objects or not body_objects:
        return

    body = body_objects[0]

    for cloth_obj in clothing_objects:
        # Shrinkwrap: wrap clothing sát vào body
        mod = cloth_obj.modifiers.new(name="Fit_Body", type='SHRINKWRAP')
        mod.target = body
        mod.offset = 0.005  # 5mm offset

        if size_override is not None:
            cloth_obj.scale = (1.0 + size_override * 0.1,) * 3


if __name__ == "__main__":
    main()
