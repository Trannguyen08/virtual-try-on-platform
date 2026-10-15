"""Blender headless script for optional GLB normalization and decimation."""

from __future__ import annotations

import sys
from pathlib import Path

import bpy


def arguments() -> tuple[Path, Path, int]:
    if "--" not in sys.argv:
        raise SystemExit("Expected: -- <source.glb> <destination.glb> <target_faces>")
    values = sys.argv[sys.argv.index("--") + 1 :]
    if len(values) != 3:
        raise SystemExit("Expected exactly three garment post-processing arguments")
    return Path(values[0]).resolve(), Path(values[1]).resolve(), int(values[2])


def main() -> None:
    source, destination, target_faces = arguments()
    if not source.is_file() or source.suffix.lower() != ".glb":
        raise SystemExit("Source must be an existing GLB file")
    if destination.suffix.lower() != ".glb":
        raise SystemExit("Destination must use the GLB extension")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(source))

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not mesh_objects:
        raise SystemExit("Imported asset contains no mesh objects")

    total_faces = sum(len(obj.data.polygons) for obj in mesh_objects)
    if target_faces > 0 and total_faces > target_faces:
        ratio = max(0.01, min(1.0, target_faces / total_faces))
        for obj in mesh_objects:
            bpy.ops.object.select_all(action="DESELECT")
            modifier = obj.modifiers.new(name="Garment3D_Decimate", type="DECIMATE")
            modifier.ratio = ratio
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.modifier_apply(modifier=modifier.name)
            obj.select_set(False)

    destination.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(destination),
        export_format="GLB",
        export_apply=True,
        export_materials="EXPORT",
    )


if __name__ == "__main__":
    main()
