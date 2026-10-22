"""Headless Blender entry point for manual body and illustrative clothing GLBs.

Run only through the validated body-builder API. Blender uses Z-up internally;
the glTF exporter converts the scene to the platform's Y-up GLB convention.
"""

import argparse
import hashlib
import importlib
import json
import re
import sys
from pathlib import Path


def arguments():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=("body", "clothing"), required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--params", required=True)
    parser.add_argument("--source")
    return parser.parse_args(argv)


def material(name, color):
    import bpy

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    rgb = tuple(int(color[index:index + 2], 16) / 255 for index in (1, 3, 5))
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*rgb, 1)
    return mat


def ellipsoid(name, location, scale, mat):
    import bpy

    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    return obj


def load_mpfb_services():
    """Enable the installed MPFB version before creating/loading native bodies."""
    import addon_utils

    services = None
    for addon in ("bl_ext.blender_org.mpfb", "bl_ext.user_default.mpfb", "mpfb"):
        try:
            addon_utils.enable(addon, default_set=False, persistent=False)
            services = importlib.import_module(f"{addon}.services")
            break
        except (ImportError, AttributeError, RuntimeError):
            continue
    if services is None:
        raise RuntimeError("MPFB_UNAVAILABLE: install and enable MPFB2 in the Blender used by the backend")
    return services


def mpfb_version(services):
    manifest = Path(services.__file__).resolve().parents[1] / "blender_manifest.toml"
    if manifest.is_file():
        match = re.search(r'^version\s*=\s*"([^"]+)"', manifest.read_text(encoding="utf-8"), re.MULTILINE)
        if match:
            return match.group(1)
    package = importlib.import_module(services.__name__.rsplit(".", 1)[0])
    return str(getattr(package, "bl_info", {}).get("version", "unknown"))


def prepare_body_export(human, services):
    """Bake only the export copy in memory, after its native scene was saved."""
    import bpy

    services.TargetService.bake_targets(human)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = human
    human.select_set(True)
    for modifier in list(human.modifiers):
        if modifier.type == "MASK":
            bpy.ops.object.modifier_apply(modifier=modifier.name)


def mpfb_body(params, skin, preserve=False):
    """Create the installed MPFB human, retaining topology for native fitting."""
    import bpy

    services = load_mpfb_services()

    HumanService = services.HumanService
    TargetService = services.TargetService
    macro = TargetService.get_default_macro_info_dict()
    macro["gender"] = {"female": 0.0, "neutral": 0.5, "male": 1.0}[params["gender"]]
    age = params["age"]
    macro["age"] = (age - 10) / 30 if age <= 25 else 0.5 + (age - 25) / 110
    macro["weight"] = max(0.0, min(1.0, (params["weight_kg"] - 35) / 60))
    macro["muscle"] = params["proportions"]["muscle_tone"]
    if params["gender"] == "neutral":
        # Match Blender's shown Larger/More firm breast preset at influence 0.10.
        macro["cupsize"] = 0.55
        macro["firmness"] = 0.55
    human = HumanService.create_human(mask_helpers=True, detailed_helpers=True,
                                      extra_vertex_groups=True, feet_on_ground=True,
                                      scale=0.1, macro_detail_dict=macro)
    proportions = dict(params["proportions"])
    measurements = params.get("measurements_cm") or {}
    height_cm = params["height_cm"]
    physical_targets = {
        "shoulder_width": ("shoulder_width_cm", 0.247, 24.0),
        "chest": ("chest_cm", 0.53, 34.0),
        "waist": ("waist_cm", 0.45, 34.0),
        "hips": ("hip_cm", 0.55, 34.0),
        "leg_length": ("inseam_cm", 0.47, 26.0),
    }
    for proportion, (measurement, height_ratio, span_cm) in physical_targets.items():
        value_cm = measurements.get(measurement)
        if value_cm is not None:
            baseline_cm = height_cm * height_ratio
            proportions[proportion] = max(
                0.0, min(1.0, 0.5 + (value_cm - baseline_cm) / span_cm)
            )

    targets = {
        "shoulder_width": "measure-shoulder-dist",
        "waist": "measure-waist-circ",
        "hips": "measure-hips-circ",
        "chest": "measure-bust-circ",
        "belly": "stomach-pregnant",
        "leg_length": ("measure-upperleg-height", "measure-lowerleg-height"),
        "arm_length": ("measure-upperarm-length", "measure-lowerarm-length"),
        "buttocks": "buttocks-volume",
    }
    morphs = []
    for key, target in targets.items():
        value = proportions[key]
        if value != 0.5:
            for name in (target,) if isinstance(target, str) else target:
                morphs.append({"target": f"{name}-{'incr' if value > 0.5 else 'decr'}",
                               "value": abs(value - 0.5) * 2})
    if morphs:
        TargetService.bulk_load_targets(human, morphs)
    if not preserve:
        prepare_body_export(human, services)
    # Scale from actual bounds instead of assuming a fixed MPFB height.
    bpy.context.view_layer.update()
    from mathutils import Vector
    evaluated = human.evaluated_get(bpy.context.evaluated_depsgraph_get())
    corners = [evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box]
    height = max(v.z for v in corners) - min(v.z for v in corners)
    if height <= 0:
        raise ValueError("MPFB returned an empty human")
    factor = params["height_cm"] / 100 / height
    human.scale = tuple(axis * factor for axis in human.scale)
    bpy.context.view_layer.update()
    evaluated = human.evaluated_get(bpy.context.evaluated_depsgraph_get())
    corners = [evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box]
    human.location.z -= min(v.z for v in corners)
    human.data.materials.clear()
    human.data.materials.append(skin)
    return human, services


def make_body(params, native_output=None):
    import bpy

    skin = material("Skin", params["skin_color"])
    human, services = mpfb_body(params, skin, preserve=native_output is not None)
    if native_output is not None:
        human["vto_native_body"] = True
        bpy.context.scene["vto_native_version"] = 1
        bpy.context.scene["vto_body_parameters"] = json.dumps(params, sort_keys=True)
        bpy.context.scene["vto_blender_version"] = bpy.app.version_string
        bpy.context.scene["vto_mpfb_services"] = services.__name__
        bpy.context.scene["vto_mpfb_version"] = mpfb_version(services)
        bpy.context.scene["vto_body_script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        Path(native_output).parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(native_output), check_existing=False, compress=True)
        prepare_body_export(human, services)
    print("BODY_METHOD=mpfb")


def make_native_clothing(params, source, entry):
    """Fit MHCLO onto the original MPFB topology instead of reimported GLB."""
    import bpy
    from garment.mpfb.blender_fitting import fit_native_garments

    native = Path(source).with_suffix(".blend")
    if not native.is_file():
        raise ValueError("BODY_REFIT_DATA_MISSING: create a new body with native MPFB data")
    services = load_mpfb_services()
    bpy.ops.wm.open_mainfile(filepath=str(native), load_ui=False, use_scripts=False)
    services = load_mpfb_services()
    if (bpy.context.scene.get("vto_native_version") != 1
            or bpy.context.scene.get("vto_blender_version") != bpy.app.version_string
            or bpy.context.scene.get("vto_mpfb_services") != services.__name__
            or bpy.context.scene.get("vto_mpfb_version") != mpfb_version(services)):
        raise ValueError("BODY_REFIT_VERSION_MISMATCH: create a new body with this Blender/MPFB")
    humans = [obj for obj in bpy.context.scene.objects
              if obj.type == "MESH" and obj.get("vto_native_body")]
    if len(humans) != 1 or not humans[0].data.shape_keys:
        raise ValueError("BODY_REFIT_DATA_INVALID: expected one unbaked MPFB basemesh")
    human = humans[0]
    report = fit_native_garments(human, services, entry, params)
    report["body_job_id"] = Path(source).stem
    report["body_scene_sha256"] = hashlib.sha256(native.read_bytes()).hexdigest()
    report["body_generator_sha256"] = bpy.context.scene.get("vto_body_script_sha256")
    prepare_body_export(human, services)
    print("CLOTHING_METHOD=mpfb_refit")
    return report


def make_clothing(params, source):
    import bpy

    if not source or not Path(source).is_file():
        raise ValueError("Body source GLB is missing")
    repo_root = str(Path(__file__).resolve().parents[2])
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from garment.mpfb.catalog import load_catalog

    entry = load_catalog().get(params["garment_id"])
    if entry is not None:
        if entry.get("engine") == "gltf_reference":
            from garment.external.alignment import make_reference_clothing

            return make_reference_clothing(params, source, entry)
        return make_native_clothing(params, source, entry)
    bpy.ops.import_scene.gltf(filepath=source)
    body_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not body_objects:
        raise ValueError("Body source GLB has no mesh")
    from mathutils import Vector
    highest = max((obj.matrix_world @ Vector(corner)).z
                  for obj in body_objects for corner in obj.bound_box)
    factor = highest / 1.7
    cloth = material("Illustrative clothing", params["color_hex"])
    clothing_start = {obj.name for obj in bpy.context.scene.objects}
    assets_dir = Path(__file__).resolve().parents[2] / "data" / "external" / "clothing"
    garment_id = params["garment_id"]
    asset_glb = assets_dir / f"{garment_id}.glb"
    asset_obj = assets_dir / f"{garment_id}.obj"
    loaded_asset = False
    if asset_glb.is_file():
        bpy.ops.import_scene.gltf(filepath=str(asset_glb))
        loaded_asset = True
    elif asset_obj.is_file():
        if hasattr(bpy.ops.wm, "obj_import"):
            bpy.ops.wm.obj_import(filepath=str(asset_obj))
        else:
            bpy.ops.import_scene.obj(filepath=str(asset_obj))
        loaded_asset = True
    if loaded_asset and not any(obj.name not in clothing_start and obj.type == "MESH"
                                for obj in bpy.context.scene.objects):
        raise ValueError("Clothing asset contains no mesh")
    category = params["category"]
    if loaded_asset:
        print("CLOTHING_METHOD=asset")
    elif category == "t_shirt":
        # Blender executes this file directly, so expose the repository package.
        repo_root = str(Path(__file__).resolve().parents[2])
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        from garment.mesh.blender_tshirt import create_tshirt

        cloth.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.85
        create_tshirt(body_objects, cloth, params["size"])
        # Remains illustrative in the API: no real draping or measured fit.
        print("CLOTHING_METHOD=synthetic_tshirt")
        return
    elif category == "pants":
        for side in (-1, 1):
            ellipsoid(f"Clothing_Pants_{side}", (side * 0.12 * factor, 0, 0.42 * factor),
                      (0.105 * factor, 0.105 * factor, 0.39 * factor), cloth)
    elif category == "dress":
        bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.38 * factor,
                                        radius2=0.16 * factor, depth=0.95 * factor,
                                        location=(0, 0, 0.85 * factor))
        bpy.context.object.name = "Clothing_Dress"
        bpy.context.object.data.materials.append(cloth)
    else:
        ellipsoid("Clothing_Top", (0, 0, 1.15 * factor),
                  (0.27 * factor, 0.19 * factor, 0.32 * factor), cloth)
        for side in (-1, 1):
            ellipsoid(f"Clothing_Sleeve_{side}",
                      (side * 0.28 * factor, 0, 1.27 * factor),
                      (0.09 * factor, 0.1 * factor, 0.14 * factor), cloth)
    size_scale = {"XS": 0.90, "S": 0.95, "M": 1.0, "L": 1.05,
                  "XL": 1.10, "XXL": 1.15}[params["size"]]
    if loaded_asset:
        for obj in bpy.context.scene.objects:
            if obj.name not in clothing_start and (obj.parent is None or obj.parent.name in clothing_start):
                obj.scale = tuple(value * factor for value in obj.scale)
                obj.location = tuple(value * factor for value in obj.location)
    for obj in bpy.context.scene.objects:
        if obj.name not in clothing_start and obj.type == "MESH":
            # Keep authored textures/materials on imported garment assets.
            if not loaded_asset or not obj.data.materials:
                obj.data.materials.clear()
                obj.data.materials.append(cloth)
            obj.scale.x *= size_scale
            obj.scale.y *= size_scale


def main():
    import bpy

    args = arguments()
    params = json.loads(args.params)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = None
    if args.action == "body":
        make_body(params, native_output=output.with_suffix(".blend"))
    else:
        report = make_clothing(params, args.source)
    bpy.ops.export_scene.gltf(filepath=args.output, export_format="GLB",
                              export_apply=True, export_yup=True, export_morph=False)
    if report is not None:
        output.with_suffix(".refit.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
