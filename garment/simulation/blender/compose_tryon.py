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
    parser.add_argument("--garment", action="append", required=True)
    parser.add_argument("--metadata", action="append", required=True)
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


def ray_surface_depth(trees, point, side, body_depth_bounds):
    """Find the visible body surface along the shell's front/back direction."""
    from mathutils import Vector

    lower, upper = body_depth_bounds
    start_y = lower - 0.5 if side < 0 else upper + 0.5
    direction = Vector((0.0, 1.0 if side < 0 else -1.0, 0.0))
    origin = Vector((point.x, start_y, point.z))
    distance = upper - lower + 1.0
    hits = [tree.ray_cast(origin, direction, distance) for tree in trees]
    hits = [hit for hit in hits if hit and hit[0] is not None]
    return min(hits, key=lambda hit: hit[3])[0].y if hits else None


def lift_top_shoulders(garment_objects, center_x, body_height):
    """Raise low photo-derived shoulders while preserving the neck and hem."""
    from mathutils import Vector

    front = next((obj for obj in garment_objects
                  if obj.name.startswith("GarmentFront")), None)
    if front is None:
        raise ValueError("GARMENT_MESH_MISSING: front panel required")
    bin_width = 0.01
    upper_edge = {}
    for vertex in front.data.vertices:
        point = front.matrix_world @ vertex.co
        column = round((point.x - center_x) / bin_width)
        upper_edge[column] = max(upper_edge.get(column, point.z), point.z)

    max_lift = min(0.06, body_height * 0.03)
    applied_max = 0.0
    for obj in garment_objects:
        inverse = obj.matrix_world.inverted()
        for vertex in obj.data.vertices:
            point = obj.matrix_world @ vertex.co
            column = round((point.x - center_x) / bin_width)
            envelope = max(upper_edge.get(key, point.z)
                           for key in (column - 1, column, column + 1))
            distance_below_edge = max(0.0, envelope - point.z)
            edge_weight = max(0.0, 1.0 - distance_below_edge / 0.24)
            lateral_weight = min(1.0, max(
                0.0, (abs(point.x - center_x) - 0.07) / 0.04,
            ))
            sleeve_weight = min(1.0, max(
                0.0, (abs(point.x - center_x) - 0.14) / 0.15,
            ))
            lift = edge_weight * (
                max_lift * lateral_weight + 0.05 * sleeve_weight
            )
            applied_max = max(applied_max, lift)
            if lift:
                vertex.co = inverse @ Vector((point.x, point.y, point.z + lift))
        obj.data.update()
    return applied_max


def conform_sleeve_silhouette(garment_objects, body_points, metadata,
                              *, center_x, body_bottom, body_height):
    """Keep photo-derived sleeve edges close to the posed upper arms."""
    from mathutils import Vector

    landmarks = metadata.get("landmarks") or {}
    try:
        armpit_x = abs(float(
            landmarks["right_armpit"]["front_position_m"][0]
        ))
        cuff_x = abs(float(
            landmarks["right_sleeve_end"]["front_position_m"][0]
        ))
    except (KeyError, TypeError, ValueError, IndexError):
        return 0.0
    if not 0.10 < armpit_x < cuff_x:
        return 0.0

    # Past the armpit the mesh is sleeve fabric, not torso fabric. The photo
    # silhouette can hang below an A-pose arm even after depth projection.
    start_x = armpit_x + 0.015
    full_x = min(cuff_x, start_x + 0.05)
    if full_x <= start_x:
        return 0.0
    lower_body_limit = body_bottom + 0.61 * body_height
    arm_rows = {}
    for point in body_points:
        if point.z < lower_body_limit:
            continue
        offset_x = point.x - center_x
        side = 1 if offset_x >= 0 else -1
        key = (side, round(abs(offset_x) / 0.01))
        arm_rows.setdefault(key, []).append(point.z)

    envelopes = {}
    max_shift = 0.0
    for obj in garment_objects:
        inverse = obj.matrix_world.inverted()
        for vertex in obj.data.vertices:
            point = obj.matrix_world @ vertex.co
            offset_x = point.x - center_x
            lateral = abs(offset_x)
            if lateral < start_x or point.z < lower_body_limit:
                continue
            side = 1 if offset_x >= 0 else -1
            key = (side, round(lateral / 0.01))
            if key not in envelopes:
                values = sorted(value
                                for neighbor in (key[1] - 1, key[1], key[1] + 1)
                                for value in arm_rows.get((side, neighbor), ()))
                if len(values) < 12:
                    envelopes[key] = None
                else:
                    envelopes[key] = (
                        values[int(0.03 * (len(values) - 1))] - 0.012,
                        values[int(0.97 * (len(values) - 1))] + 0.012,
                    )
            envelope = envelopes[key]
            if envelope is None:
                continue
            weight = min(1.0, (lateral - start_x) / (full_x - start_x))
            target_z = min(max(point.z, envelope[0]), envelope[1])
            shift = weight * (target_z - point.z)
            if abs(shift) > 0.000001:
                vertex.co = inverse @ Vector((
                    point.x, point.y, point.z + shift,
                ))
                max_shift = max(max_shift, abs(shift))
        obj.data.update()
    return max_shift


def fit_parametric_shell(trees, garment_objects, body_depth_bounds,
                         *, category, body_bottom, body_height):
    """Wrap image-derived front/back panels around the body without lateral spikes.

    A single photograph produces a shallow shell. Nearest-triangle normal pushes
    can send neighboring vertices in unrelated directions and tear the texture.
    Depth-only projection retains every vertex's horizontal and vertical place.
    """
    from mathutils import Vector
    from mathutils.kdtree import KDTree

    front = next((obj for obj in garment_objects
                  if obj.name.startswith("GarmentFront")), None)
    back = next((obj for obj in garment_objects
                 if obj.name.startswith("GarmentBack")), None)
    if front is None or back is None:
        raise ValueError("GARMENT_MESH_MISSING: parametric front/back panels required")

    def panel_center(obj):
        return median((obj.matrix_world @ vertex.co).y
                      for vertex in obj.data.vertices)

    front_center = panel_center(front)
    back_center = panel_center(back)
    if abs(front_center - back_center) < 0.001:
        raise ValueError("GARMENT_FRAME_INVALID: front/back depth is ambiguous")
    front_side = -1 if front_center < back_center else 1
    center_y = (front_center + back_center) / 2.0
    clearance = 0.01
    projected = 0
    missed = 0
    moved = 0
    deep = 0
    large = 0
    panel_trees = {}
    # A shirt hem hangs below the pelvis. Sampling the body below this height
    # follows the gap between the legs and turns a long shirt into shorts.
    hip_floor = (body_bottom + body_height * 0.56
                 if category in {"tshirt", "shirt", "jacket", "dress"} else None)

    for obj, side in ((front, front_side), (back, -front_side)):
        original = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
        targets = []
        for point in original:
            actual_depth = ray_surface_depth(trees, point, side, body_depth_bounds)
            if hip_floor is None or point.z >= hip_floor:
                targets.append(actual_depth)
                continue
            hem_depth = ray_surface_depth(
                trees, Vector((point.x, point.y, hip_floor)),
                side, body_depth_bounds,
            )
            candidates = [depth for depth in (actual_depth, hem_depth)
                          if depth is not None]
            targets.append(max(candidates, key=lambda depth: side * depth)
                           if candidates else None)
        hits = [(index, depth) for index, depth in enumerate(targets)
                if depth is not None]
        if not hits:
            raise ValueError("SEVERE_MESH_PENETRATION: no body surface under garment panel")
        nearest_hits = KDTree(len(hits))
        for index, _depth in hits:
            point = original[index]
            nearest_hits.insert(Vector((point.x, 0.0, point.z)), index)
        nearest_hits.balance()
        inverse = obj.matrix_world.inverted()
        mapped = KDTree(len(original))
        panel_depths = []

        for index, point in enumerate(original):
            target = targets[index]
            if target is None:
                missed += 1
                _location, neighbor_index, distance = nearest_hits.find(
                    Vector((point.x, 0.0, point.z))
                )
                neighbor = original[neighbor_index]
                neighbor_depth = targets[neighbor_index]
                influence = max(0.0, 1.0 - distance / 0.08)
                target_y = point.y + influence * (
                    neighbor_depth + side * clearance - neighbor.y
                )
            else:
                projected += 1
                target_y = target + side * clearance
            panel_depths.append(target_y)

        # The ray result changes abruptly around the arm silhouette. Smooth
        # along existing mesh edges and keep every hit outside the body.
        neighbors = [[] for _vertex in obj.data.vertices]
        for edge in obj.data.edges:
            first, second = edge.vertices
            neighbors[first].append(second)
            neighbors[second].append(first)
        for _iteration in range(12):
            smoothed = []
            for index, depth in enumerate(panel_depths):
                adjacent = neighbors[index]
                value = (0.6 * depth + 0.4 *
                         sum(panel_depths[other] for other in adjacent) / len(adjacent)
                         if adjacent else depth)
                if targets[index] is not None:
                    required = targets[index] + side * clearance
                    if side * value < side * required:
                        value = required
                smoothed.append(value)
            panel_depths = smoothed

        for index, point in enumerate(original):
            target_y = panel_depths[index]
            displacement = abs(target_y - point.y)
            if displacement > 0.000001:
                moved += 1
            if displacement > 0.06:
                large += 1
            if displacement > 0.12:
                deep += 1
            obj.data.vertices[index].co = inverse @ Vector(
                (point.x, target_y, point.z)
            )
            mapped.insert(Vector((point.x, 0.0, point.z)), index)
        obj.data.update()
        mapped.balance()
        panel_trees[side] = (mapped, panel_depths)

    # The reconstruction exports side seams as a separate mesh. Reuse the
    # projected boundary depth so those faces stay attached to both panels.
    for obj in garment_objects:
        if obj is front or obj is back:
            continue
        inverse = obj.matrix_world.inverted()
        for vertex in obj.data.vertices:
            point = obj.matrix_world @ vertex.co
            side = front_side if (point.y - center_y) * front_side > 0 else -front_side
            mapped, depths = panel_trees[side]
            _location, index, distance = mapped.find(
                Vector((point.x, 0.0, point.z))
            )
            if distance > 0.002:
                raise ValueError(
                    "SEVERE_MESH_PENETRATION: seam is detached from panel"
                )
            target_y = depths[index]
            displacement = abs(target_y - point.y)
            if displacement > 0.000001:
                moved += 1
            if displacement > 0.06:
                large += 1
            if displacement > 0.12:
                deep += 1
            vertex.co = inverse @ Vector((point.x, target_y, point.z))
        obj.data.update()

    return moved, deep, large, projected, missed


def fit_garment_width_profile(garment_objects, metadata, *, category):
    """Scale the reconstructed shell by body/garment circumferences in cm."""
    fit = metadata.get("fit_settings") or {}
    mode = fit.get("mode", "auto")
    body = metadata.get("body_measurements_cm") or {}
    garment = fit.get("garment_measurements_cm") or {}
    ease_cm = float(fit.get("ease_cm", 4.0)) if mode == "auto" else 0.0
    measured = metadata.get("measurements") or {}

    def reconstructed_value(key):
        item = measured.get(key) or {}
        value = item.get("value_cm")
        return float(value) if value is not None else None

    def width_factor(target_circumference, current_flat_width):
        if not target_circumference or not current_flat_width:
            return None
        # Approximate a front-view chord from circumference using an oval torso.
        return (float(target_circumference) * 0.40) / float(current_flat_width)

    sections = []
    if category in {"tshirt", "shirt", "jacket", "dress"}:
        target_chest = (garment.get("chest_circumference_cm") if mode == "measurements"
                        else float(body.get("chest_cm") or 0) + ease_cm)
        target_waist = (garment.get("waist_circumference_cm") if mode == "measurements"
                        else float(body.get("waist_cm") or 0) + ease_cm)
        target_hem = (garment.get("hem_circumference_cm") if mode == "measurements"
                      else float(body.get("waist_cm") or 0) + ease_cm)
        if mode == "auto" and (not body.get("chest_cm") or not body.get("waist_cm")):
            raise ValueError("BODY_MEASUREMENTS_MISSING: save body measurements before auto fit")
        factors = (
            (0.68, width_factor(target_chest, reconstructed_value("chest_flat_width")), "chest"),
            (0.32, width_factor(target_waist, reconstructed_value("waist_flat_width")), "waist"),
            (0.04, width_factor(target_hem, reconstructed_value("hem_flat_width")), "hem"),
        )
        sections.extend((position, factor, section)
                        for position, factor, section in factors if factor is not None)
    elif category in {"pants", "skirt"}:
        target_waist = (garment.get("waist_circumference_cm") if mode == "measurements"
                        else float(body.get("waist_cm") or 0) + ease_cm)
        target_hip = (garment.get("hip_circumference_cm") if mode == "measurements"
                      else float(body.get("hip_cm") or 0) + ease_cm)
        if mode == "auto" and (not body.get("waist_cm") or not body.get("hip_cm")):
            raise ValueError("BODY_MEASUREMENTS_MISSING: save body measurements before auto fit")
        factors = (
            (0.98, width_factor(target_waist, reconstructed_value("waist_flat_width")), "waist"),
            (0.70, width_factor(target_hip, reconstructed_value("hip_flat_width")), "hip"),
        )
        sections.extend((position, factor, section)
                        for position, factor, section in factors if factor is not None)

    if not sections:
        raise ValueError("BODY_MEASUREMENTS_MISSING: no usable body/garment dimensions")
    for _position, factor, section in sections:
        if not 0.65 <= factor <= 1.5:
            raise ValueError(
                f"GARMENT_MEASUREMENT_MISMATCH: {section} width needs an unsafe scale"
            )

    low, high = bounds(garment_objects)
    center_x = (low[0] + high[0]) / 2
    bottom_z, top_z = low[2], high[2]
    height = top_z - bottom_z
    if height <= 0:
        raise ValueError("GARMENT_MESH_MISSING: garment has no vertical extent")
    sections.sort(key=lambda item: item[0])
    from mathutils import Vector

    for obj in garment_objects:
        inverse = obj.matrix_world.inverted()
        for vertex in obj.data.vertices:
            point = obj.matrix_world @ vertex.co
            position = min(1.0, max(0.0, (point.z - bottom_z) / height))
            if position <= sections[0][0]:
                factor = sections[0][1]
            elif position >= sections[-1][0]:
                factor = sections[-1][1]
            else:
                for first, second in zip(sections, sections[1:]):
                    if first[0] <= position <= second[0]:
                        blend = (position - first[0]) / (second[0] - first[0])
                        factor = first[1] + blend * (second[1] - first[1])
                        break
            fitted = Vector((center_x + (point.x - center_x) * factor,
                             point.y, point.z))
            vertex.co = inverse @ fitted
        obj.data.update()
    return {section: round(factor, 3) for _position, factor, section in sections}


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

    The image-derived shell uses depth projection instead. This guard protects
    the fallback normal-displacement path from accepting distorted geometry.
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
    if len(args.garment) != len(args.metadata):
        raise ValueError("GARMENT_FRAME_INVALID: each garment needs matching metadata")
    metadata_items = [json.loads(Path(path).read_text(encoding="utf-8"))
                      for path in args.metadata]
    for metadata in metadata_items:
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
    low_body, high_body = bounds(body)
    body_height = high_body[2] - low_body[2]
    if not 1.2 <= body_height <= 2.3:
        raise ValueError("BODY_SCALE_INVALID")
    body_center_x = (low_body[0] + high_body[0]) / 2
    from mathutils import Vector

    surfaces = body_surfaces(body)
    body_points = body_vertices(body)
    placements = []
    garment_objects = []
    totals = {"moved": 0, "deep": 0, "large": 0, "projected": 0, "missed": 0}
    tested_inside = []
    tested_severe = []

    for garment_path, metadata in zip(args.garment, metadata_items, strict=True):
        before = {obj.name for obj in bpy.context.scene.objects}
        bpy.ops.import_scene.gltf(filepath=garment_path)
        garment = [obj for obj in bpy.context.scene.objects
                   if obj.type == "MESH" and obj.name not in before]
        if not garment:
            raise ValueError("GARMENT_MESH_MISSING")
        garment_objects.extend(garment)
        category = metadata.get("garment_type")
        low_garment, high_garment = bounds(garment)
        anchor_fraction = 0.58 if category in {"pants", "skirt"} else 0.84
        body_center_y = torso_depth_center(
            body_points, center_x=body_center_x,
            bottom_z=low_body[2], body_height=body_height, category=category,
        )
        garment_center_x = (low_garment[0] + high_garment[0]) / 2
        garment_center_y = (low_garment[1] + high_garment[1]) / 2
        translation = (
            body_center_x - garment_center_x,
            body_center_y - garment_center_y,
            low_body[2] + anchor_fraction * body_height - high_garment[2],
        )
        for obj in garment:
            obj.matrix_world.translation += Vector(translation)
        bpy.context.view_layer.update()

        parametric = (metadata.get("reconstruction_mode") == "local_parametric"
                      and category in {"tshirt", "shirt", "jacket", "dress", "pants", "skirt"})
        shoulder_lift = (lift_top_shoulders(garment, body_center_x, body_height)
                         if parametric and category in {"tshirt", "shirt", "jacket", "dress"}
                         else 0.0)
        sleeve_conform = (conform_sleeve_silhouette(
            garment, body_points, metadata,
            center_x=body_center_x, body_bottom=low_body[2], body_height=body_height,
        ) if parametric and category in {"tshirt", "shirt"} else 0.0)
        bpy.context.view_layer.update()
        fit_profile = (fit_garment_width_profile(garment, metadata, category=category)
                       if parametric else {})
        bpy.context.view_layer.update()

        if parametric:
            moved, deep, large, projected, missed = fit_parametric_shell(
                surfaces, garment, (low_body[1], high_body[1]),
                category=category, body_bottom=low_body[2], body_height=body_height,
            )
        else:
            moved, deep, large = fit_to_body(surfaces, garment)
            projected = missed = 0
        vertex_count = sum(len(obj.data.vertices) for obj in garment)
        if not parametric:
            validate_surface_adjustment(large, vertex_count)
        bpy.context.view_layer.update()
        inside, severe = penetration_fraction(surfaces, garment)
        if severe > 0.01 or inside > 0.03 or (not parametric and deep > vertex_count * 0.05):
            raise ValueError(
                "SEVERE_MESH_PENETRATION: "
                f"inside={inside:.4f}, severe={severe:.4f}, deep={deep}"
            )
        for key, value in (("moved", moved), ("deep", deep), ("large", large),
                           ("projected", projected), ("missed", missed)):
            totals[key] += value
        tested_inside.append(inside)
        tested_severe.append(severe)
        placements.append({
            "garment_type": category,
            "placement": "body_ray_projected_shell" if parametric
            else "body_height_anchor_and_surface_clearance",
            "translation_m_blender_frame": translation,
            "fit_profile": fit_profile,
            "fit_mode": (metadata.get("fit_settings") or {}).get("mode", "auto"),
            "shoulder_lift_m": shoulder_lift,
            "sleeve_conform_m": sleeve_conform,
        })

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(output), export_format="GLB", export_apply=True,
        export_yup=True, export_materials="EXPORT",
    )
    print("TRYON_REPORT=" + json.dumps({
        "placement": "+".join(item["placement"] for item in placements),
        "garments": placements,
        "clearance_adjusted_vertices": totals["moved"],
        "large_adjustment_vertices": totals["large"],
        "deep_vertices": totals["deep"],
        "projection_hits": totals["projected"],
        "projection_misses": totals["missed"],
        "penetration_fraction": round(max(tested_inside), 6),
        "severe_penetration_fraction": round(max(tested_severe), 6),
        "shoulder_lift_max_m": round(max((item["shoulder_lift_m"] for item in placements), default=0.0), 6),
        "sleeve_conform_max_m": round(max((item["sleeve_conform_m"] for item in placements), default=0.0), 6),
        "simulation_ran": False,
    }))


if __name__ == "__main__":
    main()
