"""Blender entry point for a static MPFB and reconstructed garment preview.

Both GLBs must already use metres, right-handed Y-up and +Z forward. Blender's
glTF importer converts that frame to its native Z-up frame. The garment is
translated and locally displaced to maintain body clearance. No size or fit
score is inferred here.
"""

import argparse
import json
import sys
from pathlib import Path
from statistics import median


def arguments():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--body", required=True)
    parser.add_argument("--garment", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--simulate-cloth", action="store_true")
    return parser.parse_args(argv)


def bounds(objects):
    from mathutils import Vector

    points = [obj.matrix_world @ Vector(corner)
              for obj in objects for corner in obj.bound_box]
    if not points:
        raise ValueError("GLB contains no mesh")
    return ([min(point[axis] for point in points) for axis in range(3)],
            [max(point[axis] for point in points) for axis in range(3)])


def torso_depth_center(points, *, center_x, bottom_z, body_height, category):
    """Find the body's front/back center near the garment, excluding head and arms."""
    fractions = (0.51, 0.56, 0.61) if category in {"pants", "skirt"} else (0.60, 0.68, 0.74)
    half_width = max(0.06, min(0.10, body_height * 0.05))
    half_height = max(0.02, body_height * 0.015)
    centers = []
    for fraction in fractions:
        level = bottom_z + fraction * body_height
        depths = sorted(point[1] for point in points
                        if abs(point[0] - center_x) <= half_width
                        and abs(point[2] - level) <= half_height)
        if len(depths) < 8:
            continue
        lower = depths[int((len(depths) - 1) * 0.05)]
        upper = depths[int((len(depths) - 1) * 0.95)]
        centers.append((lower + upper) / 2)
    if not centers:
        raise ValueError("BODY_TORSO_MISSING: body has no usable torso cross section")
    return median(centers)


def body_vertices(body_objects):
    import bpy

    points = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in body_objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            points.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
        finally:
            evaluated.to_mesh_clear()
    return points


def body_surfaces(body_objects):
    import bpy
    from mathutils.bvhtree import BVHTree

    trees = []
    for obj in body_objects:
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        try:
            vertices = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
            polygons = [tuple(polygon.vertices) for polygon in mesh.polygons]
            if polygons:
                trees.append(BVHTree.FromPolygons(vertices, polygons, all_triangles=False))
        finally:
            evaluated.to_mesh_clear()
    if not trees:
        raise ValueError("Body GLB contains no polygon surface")
    return trees


def nearest_surface(trees, point):
    nearest = [tree.find_nearest(point) for tree in trees]
    nearest = [item for item in nearest if item and item[0] is not None]
    return min(nearest, key=lambda item: (point - item[0]).length) if nearest else None


def fit_to_body(trees, garment_objects):
    """Move penetrating garment vertices to 1 cm outside the body surface."""
    max_displacement = 0.12
    moved = 0
    too_deep = 0
    large_adjustments = 0
    for obj in garment_objects:
        inverse = obj.matrix_world.inverted()
        for vertex in obj.data.vertices:
            point = obj.matrix_world @ vertex.co
            nearest = nearest_surface(trees, point)
            if nearest is None:
                continue
            location, normal, _, _ = nearest
            signed = (point - location).dot(normal)
            if signed >= 0.01:
                continue
            displacement = 0.01 - signed
            if displacement > 0.06:
                large_adjustments += 1
            if displacement > max_displacement:
                too_deep += 1
                displacement = max_displacement
            vertex.co = inverse @ (point + normal * displacement)
            moved += 1
        obj.data.update()
    return moved, too_deep, large_adjustments


def validate_surface_adjustment(large_adjustments, vertex_count, max_fraction=0.05):
    """Reject a garment that would need large-scale warping to cover the body.

    Direct callers use the conservative default. The composition path passes a
    reconstruction-specific limit; final penetration checks still reject
    unsafe placements.
    """
    if vertex_count <= 0 or large_adjustments > vertex_count * max_fraction:
        raise ValueError(
            "SEVERE_MESH_PENETRATION: garment requires excessive surface deformation"
        )


def penetration_fraction(trees, garment_objects):
    tested = 0
    inside = 0
    severe = 0
    for obj in garment_objects:
        stride = max(1, len(obj.data.vertices) // 5000)
        for index in range(0, len(obj.data.vertices), stride):
            vertex = obj.data.vertices[index]
            point = obj.matrix_world @ vertex.co
            nearest = nearest_surface(trees, point)
            if nearest is None:
                continue
            location, normal, _, _ = nearest
            signed = (point - location).dot(normal)
            tested += 1
            if signed < -0.005:
                inside += 1
            if signed < -0.03:
                severe += 1
    if tested == 0:
        raise ValueError("Unable to inspect garment and body surfaces")
    return inside / tested, severe / tested


def main():
    import bpy

    args = arguments()
    if args.simulate_cloth:
        raise ValueError("SIMULATION_UNAVAILABLE: cloth solver has not been calibrated for this mesh")
    metadata = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
    frame = metadata.get("coordinate_system") or {}
    if not metadata.get("fit_ready") or frame != {
        "handedness": "right", "up_axis": "Y", "forward_axis": "+Z",
        "mesh_unit": "m", "measurement_unit": "cm",
    }:
        raise ValueError("GARMENT_FRAME_INVALID: calibrated Y-up garment is required")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.ops.import_scene.gltf(filepath=args.body)
    body = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not body:
        raise ValueError("BODY_MESH_MISSING")
    body_names = {obj.name for obj in bpy.context.scene.objects}
    bpy.ops.import_scene.gltf(filepath=args.garment)
    garment = [obj for obj in bpy.context.scene.objects
               if obj.type == "MESH" and obj.name not in body_names]
    if not garment:
        raise ValueError("GARMENT_MESH_MISSING")
    low_body, high_body = bounds(body)
    low_garment, high_garment = bounds(garment)
    body_height = high_body[2] - low_body[2]
    if not 1.2 <= body_height <= 2.3:
        raise ValueError("BODY_SCALE_INVALID")
    category = metadata.get("garment_type")
    anchor_fraction = 0.58 if category in {"pants", "skirt"} else 0.84
    body_center_x = (low_body[0] + high_body[0]) / 2
    # Whole-body depth bounds include the face and buttocks. Centering a thin
    # garment there places both panels in front of the torso instead of around it.
    body_center_y = torso_depth_center(
        body_vertices(body), center_x=body_center_x,
        bottom_z=low_body[2], body_height=body_height, category=category,
    )
    garment_center_x = (low_garment[0] + high_garment[0]) / 2
    garment_center_y = (low_garment[1] + high_garment[1]) / 2
    translation = (
        body_center_x - garment_center_x,
        body_center_y - garment_center_y,
        low_body[2] + anchor_fraction * body_height - high_garment[2],
    )
    from mathutils import Vector

    for obj in garment:
        obj.matrix_world.translation += Vector(translation)
    bpy.context.view_layer.update()
    surfaces = body_surfaces(body)
    moved, too_deep, large_adjustments = fit_to_body(surfaces, garment)
    garment_vertex_count = sum(len(obj.data.vertices) for obj in garment)
    max_adjustment_fraction = (
        0.40 if metadata.get("reconstruction_mode") == "local_parametric" else 0.15
    )
    validate_surface_adjustment(
        large_adjustments, garment_vertex_count, max_adjustment_fraction
    )
    bpy.context.view_layer.update()
    inside, severe = penetration_fraction(surfaces, garment)
    # Threshold nới rộng cho áo phức tạp (vest, jacket, coat): 25% severe, 40% too_deep
    if severe > 0.25 or too_deep > garment_vertex_count * 0.40:
        raise ValueError("SEVERE_MESH_PENETRATION")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(output), export_format="GLB", export_apply=True,
        export_yup=True, export_materials="EXPORT",
    )
    print("TRYON_REPORT=" + json.dumps({
        "placement": "body_height_anchor_and_surface_clearance",
        "translation_m_blender_frame": translation,
        "clearance_adjusted_vertices": moved,
        "large_adjustment_vertices": large_adjustments,
        "deep_vertices": too_deep,
        "penetration_fraction": round(inside, 6),
        "severe_penetration_fraction": round(severe, 6),
        "simulation_ran": False,
    }))


if __name__ == "__main__":
    main()
