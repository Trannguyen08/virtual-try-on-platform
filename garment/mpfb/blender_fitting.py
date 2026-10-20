"""MHCLO fitting against the native basemesh; no size/fit-score claims."""

import hashlib
import importlib
import json
import math
from pathlib import Path

from .catalog import asset_dependencies, asset_root, resolve_assets, validate_choice


def validate_mapping(mapping, body_vertices, garment_vertices=None):
    """Reject incompatible indices instead of MPFB silently skipping vertices."""
    if not mapping.verts or any(index < 0 or index >= body_vertices
                                 for match in mapping.verts.values() for index in match["verts"]):
        raise ValueError("MHCLO_TOPOLOGY_MISMATCH: mapping references missing body vertices")
    for match in mapping.verts.values():
        if any(not math.isfinite(value) for value in (*match["weights"], *match["offsets"])):
            raise ValueError("MHCLO_TOPOLOGY_MISMATCH: non-finite fitting weights or offsets")
    for scaling in (mapping.x_scale, mapping.y_scale, mapping.z_scale):
        if scaling and (min(scaling[:2]) < 0 or max(scaling[:2]) >= body_vertices
                        or not math.isfinite(scaling[2]) or scaling[2] <= 0):
            raise ValueError("MHCLO_TOPOLOGY_MISMATCH: invalid body scale references")
    if garment_vertices is not None and len(mapping.verts) != garment_vertices:
        raise ValueError("MHCLO_TOPOLOGY_MISMATCH: mapping does not cover garment vertices")


def fit_native_garments(human, services, entry, parameters):
    import bpy
    from mathutils import Matrix

    validate_choice(entry, parameters["category"], parameters["size"])
    paths = resolve_assets(entry)
    mhclo_type = importlib.import_module(
        services.__name__.rsplit(".", 1)[0] + ".entities.clothes.mhclo"
    ).Mhclo
    assets = []
    for path in paths:
        mapping = mhclo_type()
        mapping.load(str(path))
        count = len(human.data.vertices)
        validate_mapping(mapping, count)
        clothes = services.HumanService.add_mhclo_asset(
            str(path), human, asset_type="Clothes", subdiv_levels=0,
            material_type="GAMEENGINE", set_up_rigging=False,
        )
        if clothes is None or clothes.type != "MESH" or not clothes.data.vertices:
            raise ValueError("MHCLO_FIT_INVALID: garment contains no mesh")
        if len(clothes.data.vertices) > 30000:
            raise ValueError("MHCLO_FIT_INVALID: garment exceeds 30000 vertices")
        validate_mapping(mapping, count, len(clothes.data.vertices))
        # Fitting uses basemesh LOCAL coordinates. Inherit the body's actual
        # height transform exactly once; never scale the garment by size again.
        clothes.parent = human
        clothes.matrix_parent_inverse = Matrix.Identity(4)
        clothes.location = (0, 0, 0)
        clothes.rotation_euler = (0, 0, 0)
        clothes.scale = (1, 1, 1)
        if any(not math.isfinite(value) for vertex in clothes.data.vertices for value in vertex.co):
            raise ValueError("MHCLO_FIT_INVALID: garment contains non-finite coordinates")
        for polygon in clothes.data.polygons:
            polygon.use_smooth = True
        clothes["vto_garment_source"] = "mhclo_body_refit"
        assets.append({"path": path.relative_to(asset_root()).as_posix(),
                       "mhclo_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                       "files": [{"path": file.relative_to(asset_root()).as_posix(),
                                  "sha256": hashlib.sha256(file.read_bytes()).hexdigest()}
                                 for file in asset_dependencies(path, asset_root())],
                       "vertices": len(clothes.data.vertices)})
    bpy.context.view_layer.update()
    return {
        "version": 1,
        "garment_id": entry["id"], "mode": "body_refit",
        "method": "blender_mpfb_refit", "source": "module",
        "assets": assets, "asset_license": entry["license"], "asset_source": entry["source"],
        "requested_size": parameters["size"], "size_chart_verified": False,
        "cloth_simulation": False, "fit_score": None,
        "body_occlusion_masks": True, "material_mode": "original_gameengine",
        "body_parameters": json.loads(bpy.context.scene["vto_body_parameters"]),
        "blender_version": bpy.app.version_string, "mpfb_services": services.__name__,
        "mpfb_version": bpy.context.scene.get("vto_mpfb_version"),
        "pipeline_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "catalog_entry_sha256": hashlib.sha256(json.dumps(entry, sort_keys=True).encode("utf-8")).hexdigest(),
        "export_frame": "metres,Y-up,+Z-forward",
    }
