"""Blender adapter for the synthetic body-aware T-shirt template."""

import math

from garment.mesh.tshirt_geometry import build_tshirt
from garment.mesh.torso_sections import TorsoSections


def create_tshirt(body_objects, material, size):
    import bmesh
    import bpy

    # Evaluate meshes so modifiers and world transforms match the exported body.
    points, polygons = [], []
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in body_objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            offset = len(points)
            points.extend(evaluated.matrix_world @ v.co for v in mesh.vertices)
            mesh.calc_loop_triangles()
            polygons.extend(tuple(offset + i for i in p.vertices) for p in mesh.loop_triangles)
        finally:
            evaluated.to_mesh_clear()
    if not points or not polygons:
        raise ValueError("Cannot create T-shirt on an empty body")
    floor = min(p.z for p in points)
    height = max(p.z for p in points) - floor
    if not math.isfinite(height) or height <= 0:
        raise ValueError("Body has invalid height")
    sections = TorsoSections(points, polygons, height)
    anchor = next((level for level in (0.53, 0.57, 0.61)
                   if sections.section(floor + level * height)), None)
    if anchor is None:
        raise ValueError("No torso triangle cuts at hip/waist; "
                         f"body height={height:.4f}m, vertices={len(points)}, "
                         f"triangles={len(polygons)}")
    center = sections.center(floor + anchor * height)

    directions = {}
    for side in (-1, 1):
        # Outer upper-body points locate the arms in MPFB's rest pose.
        arm = [p for p in points
               if 0.19 * height < side * (p.x - center[0]) < 0.25 * height
               and p.z > floor + 0.55 * height]
        if not arm:
            raise ValueError("Cannot locate arm for T-shirt; use the MPFB rest pose")
        arm_x = sum(p.x for p in arm) / len(arm)
        arm_z = sum(p.z for p in arm) / len(arm)
        directions[side] = (arm_x - center[0] - side * 0.13 * height,
                            arm_z - floor - 0.765 * height)
    def shoulder_height(x, y):
        return sections.surface_height(x, y, floor + 0.74 * height, floor + 0.87 * height)

    vertices, faces = build_tshirt(height, floor, center, sections.radius, directions, size,
                                   sample_center=sections.center,
                                   sample_shoulder_height=shoulder_height)
    print("TSHIRT_PROFILE_METHOD=triangle_section_convex_envelope")
    print("TSHIRT_HEM_METHOD=measured_hip_profile_extension")
    mesh = bpy.data.meshes.new("Synthetic_TShirt_Surface")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(mesh)
    finally:
        bm.free()
    shirt = bpy.data.objects.new("Clothing_TShirt_Template", mesh)
    bpy.context.collection.objects.link(shirt)
    shirt.data.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    # No subdivision: preserve the sampled clearance and open boundaries.
    thickness = shirt.modifiers.new("Fabric thickness", "SOLIDIFY")
    thickness.thickness = 0.0015
    thickness.offset = 1
    shirt["garment_source"] = "synthetic_body_aware_template"
    shirt["cloth_simulation"] = False
    return shirt
