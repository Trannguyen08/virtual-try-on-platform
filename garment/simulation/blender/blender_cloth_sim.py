"""
Script: garment.simulation.blender.blender_cloth_sim
Task ID: GAR-05, GAR-06
Test Case ID: TC-GAR-05, TC-GAR-06

Script chạy trong môi trường Blender Headless (CLI không giao diện).
Cấu hình mô phỏng vật lý vải (Cloth Physics):
- Body: Collision modifier (khoảng cách chống lẹm 5mm).
- Garment: Cloth modifier (Cotton preset: mass 0.2, tension 18, bending 0.75).
- Chạy 40 frame tĩnh và xuất mesh hoàn chỉnh ra file .glb.
"""

import argparse
import sys
from pathlib import Path


def run_blender_simulation() -> None:
    try:
        import bpy
    except ImportError:
        print("[!] Lỗi: Script này chỉ chạy được bên trong môi trường Blender python (bpy).")
        sys.exit(1)

    # Tách argument truyền qua dấu '--' trong lệnh CLI của Blender
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="Blender Headless Cloth Simulation")
    parser.add_argument("--body", type=str, required=True, help="Đường dẫn file body.obj hoặc body.glb")
    parser.add_argument("--garment", type=str, required=True, help="Đường dẫn file garment.obj hoặc garment.glb")
    parser.add_argument("--output", type=str, required=True, help="Đường dẫn file output draped.glb")
    parser.add_argument("--frames", type=int, default=40, help="Số frame mô phỏng (mặc định 40)")
    parser.add_argument("--mass", type=float, default=0.20, help="Khối lượng vải (kg/m2)")
    parser.add_argument("--tension", type=float, default=18.0, help="Độ cứng kéo căng vải")
    parser.add_argument("--bending", type=float, default=0.75, help="Độ cứng uốn nếp vải")
    args = parser.parse_args(argv)

    body_path = Path(args.body).resolve()
    garment_path = Path(args.garment).resolve()
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not body_path.is_file():
        print(f"[!] Không tìm thấy file body: {body_path}")
        sys.exit(1)
    if not garment_path.is_file():
        print(f"[!] Không tìm thấy file garment: {garment_path}")
        sys.exit(1)

    # 1. Dọn sạch scene mặc định của Blender
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 2. Import Body Mesh
    if body_path.suffix.lower() == ".glb" or body_path.suffix.lower() == ".gltf":
        bpy.ops.import_scene.gltf(filepath=str(body_path))
    else:
        try:
            bpy.ops.wm.obj_import(filepath=str(body_path))
        except AttributeError:
            bpy.ops.import_scene.obj(filepath=str(body_path))

    body_obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
    if not body_obj:
        print("[!] Không nạp được body mesh.")
        sys.exit(1)
    body_obj.name = "BodyCollider"

    # Gán Collision modifier cho Body
    collision_mod = body_obj.modifiers.new(name="BodyCollision", type="COLLISION")
    collision_mod.collision.thickness_outer = 0.005  # 5 mm
    collision_mod.collision.friction = 0.50

    # 3. Import Garment Mesh
    bpy.ops.object.select_all(action="DESELECT")
    if garment_path.suffix.lower() == ".glb" or garment_path.suffix.lower() == ".gltf":
        bpy.ops.import_scene.gltf(filepath=str(garment_path))
    else:
        try:
            bpy.ops.wm.obj_import(filepath=str(garment_path))
        except AttributeError:
            bpy.ops.import_scene.obj(filepath=str(garment_path))

    garment_obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
    if not garment_obj:
        print("[!] Không nạp được garment mesh.")
        sys.exit(1)
    garment_obj.name = "GarmentCloth"

    # Gán Cloth modifier cho Garment
    cloth_mod = garment_obj.modifiers.new(name="ClothPhysics", type="CLOTH")
    settings = cloth_mod.settings
    settings.mass = args.mass
    settings.tension_stiffness = args.tension
    settings.compression_stiffness = args.tension
    settings.bending_stiffness = args.bending
    settings.air_damping = 1.0

    # Cấu hình va chạm của vải
    collision_settings = cloth_mod.collision_settings
    collision_settings.use_collision = True
    collision_settings.distance_min = 0.005  # 5 mm
    collision_settings.use_self_collision = True
    collision_settings.self_distance_min = 0.005

    # 4. Chạy mô phỏng timeline qua các frame
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = args.frames

    for f in range(1, args.frames + 1):
        scene.frame_set(f)

    # 5. Áp dụng trạng thái biến dạng ở frame cuối cùng
    depsgraph = bpy.context.evaluated_depsgraph_get()
    garment_eval = garment_obj.evaluated_get(depsgraph)
    mesh_eval = bpy.data.meshes.new_from_object(garment_eval)

    final_obj = bpy.data.objects.new("DrapedFinal", mesh_eval)
    bpy.context.collection.objects.link(final_obj)

    # Chọn duy nhất final_obj để xuất
    bpy.ops.object.select_all(action="DESELECT")
    final_obj.select_set(True)
    bpy.context.view_layer.objects.active = final_obj

    # 6. Xuất ra file GLB
    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        use_selection=True,
        export_format="GLB",
        export_yup=True,
    )
    print(f"[+] Mô phỏng Blender thành công! File xuất: {output_path}")
    sys.exit(0)


if __name__ == "__main__":
    run_blender_simulation()
