"""Preserve authored garments; align their reference frame to a body.

This is not MHCLO refitting, cloth simulation, or a size recommendation.
"""

import hashlib
import json
import math

from garment.mpfb.catalog import resolve_assets, validate_choice


def reference_scale(body_height_m, reference_height_cm):
    if not all(math.isfinite(v) and v > 0 for v in (body_height_m, reference_height_cm)):
        raise ValueError("EXTERNAL_ALIGNMENT_INVALID: heights must be finite and positive")
    return body_height_m / (reference_height_cm / 100)


def make_reference_clothing(parameters, source, entry):
    import bpy
    from mathutils import Matrix, Vector

    validate_choice(entry, parameters["category"], parameters["size"])
    paths = resolve_assets(entry)
    bpy.ops.import_scene.gltf(filepath=str(source))
    bodies = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not bodies:
        raise ValueError("EXTERNAL_ALIGNMENT_INVALID: missing body mesh")
    bpy.context.view_layer.update()
    corners = [obj.matrix_world @ Vector(corner) for obj in bodies for corner in obj.bound_box]
    floor, top = min(p.z for p in corners), max(p.z for p in corners)
    factor = reference_scale(top - floor, entry["reference_height_cm"])
    cx = (min(p.x for p in corners) + max(p.x for p in corners)) / 2
    cy = (min(p.y for p in corners) + max(p.y for p in corners)) / 2
    offset = entry.get("offset_m", [0, 0, 0])
    transform = (Matrix.Translation((cx + offset[0], cy + offset[1], floor + offset[2]))
                 @ Matrix.Rotation(math.radians(entry.get("yaw_degrees", 0)), 4, "Z")
                 @ Matrix.Scale(factor, 4))
    files = []
    for path in paths:
        before = set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(path))
        bpy.context.view_layer.update()
        imported = set(bpy.context.scene.objects) - before
        meshes = [obj for obj in imported if obj.type == "MESH"]
        if not meshes:
            raise ValueError("EXTERNAL_ALIGNMENT_INVALID: asset contains no garment mesh")
        for obj in meshes:
            world = obj.matrix_world.copy()
            obj.parent = None
            obj.matrix_world = transform @ world
            obj["vto_garment_source"] = "external_reference_alignment"
            if any(not math.isfinite(v) for vertex in obj.data.vertices for v in vertex.co):
                raise ValueError("EXTERNAL_ALIGNMENT_INVALID: non-finite garment coordinates")
        for obj in imported:
            if obj.type != "MESH":
                bpy.data.objects.remove(obj, do_unlink=True)
        files.append({"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                      "vertices": sum(len(obj.data.vertices) for obj in meshes),
                      "meshes": len(meshes)})
    bpy.context.view_layer.update()
    print("CLOTHING_METHOD=gltf_reference")
    return {"version": 1, "garment_id": entry["id"], "method": "blender_gltf_reference",
            "mode": "reference_alignment", "source": "module", "assets": files,
            "body_height_m": top - floor, "reference_height_cm": entry["reference_height_cm"],
            "scale": factor, "offset_m": offset, "yaw_degrees": entry.get("yaw_degrees", 0),
            "requested_size": parameters["size"], "size_chart_verified": False,
            "cloth_simulation": False, "fit_score": None, "body_occlusion_masks": False,
            "pose_matched": False, "material_mode": "original",
            "notes": ["Uniform height alignment only. Source garment pose is preserved; shoulders/arms may not match body."]}
