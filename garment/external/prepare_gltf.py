"""User-run Blender utility: package an externalized CLO glTF for preview.

No fitting, simulation or topology reduction is performed. Original files stay intact.
Run Blender --background --python garment/external/prepare_gltf.py
"""

import hashlib
import json
from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/external/cgtrader/dg100024/source/DG100024.gltf"
OUTPUT = ROOT / "data/external/mpfb/dg100024/dg100024.glb"


def local_file(base, reference):
    candidate = (base / reference).resolve()
    if not candidate.is_relative_to(base.resolve()) or not candidate.is_file():
        raise ValueError("Missing or unsafe local glTF dependency")
    return candidate


def prepare(source=SOURCE, output=OUTPUT):
    import bpy

    source, output = Path(source), Path(output)
    document = json.loads(source.read_text(encoding="utf-8-sig"))
    if document.get("asset", {}).get("version") != "2.0":
        raise ValueError("Expected glTF 2.0")
    buffers = document.get("buffers", [])
    if len(buffers) != 1 or buffers[0].get("uri", "").startswith("data:"):
        raise ValueError("Expected one externalized geometry buffer")
    payload = bytearray(local_file(source.parent, buffers[0]["uri"]).read_bytes())
    if len(payload) != buffers[0]["byteLength"]:
        raise ValueError("Geometry buffer length mismatch")

    cloth = [i for i, node in enumerate(document["nodes"]) if node.get("name") == "Cloth"]
    if len(cloth) != 1:
        raise ValueError("Expected a unique Cloth node; inspect source hierarchy")
    reachable = set()

    def visit(index):
        if index in reachable:
            return
        reachable.add(index)
        for child in document["nodes"][index].get("children", []):
            visit(child)

    visit(cloth[0])
    retained = sorted(reachable)
    remap = {old: new for new, old in enumerate(retained)}
    nodes = [document["nodes"][i] for i in retained]
    for node in nodes:
        if "skin" in node:
            raise ValueError("Skinned source requires a different preparation workflow")
        if "children" in node:
            node["children"] = [remap[i] for i in node["children"]]
    nodes.append({"name": "Explicit_cm_to_m", "scale": [0.01, 0.01, 0.01],
                  "children": [remap[cloth[0]]]})
    document["nodes"] = nodes
    document["scenes"] = [{"name": "Garment only", "nodes": [len(nodes) - 1]}]
    document["scene"] = 0
    for key in ("skins", "animations", "cameras"):
        document.pop(key, None)
    document.get("extensions", {}).pop("KHR_lights_punctual", None)
    for key in ("extensionsUsed", "extensionsRequired"):
        if key in document:
            document[key] = [value for value in document[key] if value != "KHR_lights_punctual"]

    output.parent.mkdir(parents=True, exist_ok=True)
    texture_sizes = []
    for index, texture in enumerate(document.get("images", [])):
        original = local_file(source.parent, texture["uri"])
        loaded = bpy.data.images.load(str(original), check_existing=False)
        optimized = output.parent / f"texture-{index:02d}.png"
        try:
            width, height = loaded.size
            factor = min(1.0, 2048 / max(width, height))
            loaded.scale(max(1, round(width * factor)), max(1, round(height * factor)))
            loaded.filepath_raw = str(optimized)
            loaded.file_format = "PNG"
            loaded.save()
            texture_sizes.append({"source": [width, height], "prepared": list(loaded.size)})
        finally:
            bpy.data.images.remove(loaded)
        payload.extend(b"\0" * (-len(payload) % 4))
        encoded = optimized.read_bytes()
        view = len(document["bufferViews"])
        document["bufferViews"].append({"buffer": 0, "byteOffset": len(payload),
                                      "byteLength": len(encoded)})
        payload.extend(encoded)
        texture.pop("uri")
        texture.update(bufferView=view, mimeType="image/png")

    document["buffers"] = [{"byteLength": len(payload)}]
    metadata = json.dumps(document, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    metadata += b" " * (-len(metadata) % 4)
    payload.extend(b"\0" * (-len(payload) % 4))
    length = 12 + 8 + len(metadata) + 8 + len(payload)
    temporary = output.with_suffix(".glb.tmp")
    with temporary.open("wb") as stream:
        stream.write(struct.pack("<4sII", b"glTF", 2, length))
        stream.write(struct.pack("<II", len(metadata), 0x4E4F534A))
        stream.write(metadata)
        stream.write(struct.pack("<II", len(payload), 0x004E4942))
        stream.write(payload)
    temporary.replace(output)
    positions = {p["attributes"]["POSITION"] for mesh in document["meshes"]
                 for p in mesh["primitives"]}
    counts = [document["accessors"][i]["count"] for i in positions]
    report = {
        "units": "m", "up": "Y", "source_units": "cm; operator assumption, unverified",
        "reference_height_cm": 180, "reference_height_verified": False,
        "source": str(source.relative_to(ROOT)), "texture_sizes": texture_sizes,
        "mesh_count": len(document["meshes"]), "unique_position_vertices": sum(counts),
        "max_position_accessor_vertices": max(counts, default=0),
        "topology_reduced": False, "vertex_budget_verified": False,
        "pose_matched": False, "cloth_simulation": False, "render_verified": False,
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "bytes": output.stat().st_size,
    }
    output.with_suffix(".prepared.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("GARMENT_PREPARED=" + str(output))
    print("Restart backend and select cgtrader-dg100024; reference alignment only.")


if __name__ == "__main__":
    prepare()
