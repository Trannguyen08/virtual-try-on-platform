"""Generate deterministic, plainly synthetic GLB 2.0 fixtures using stdlib only.

Run from the repo root: python scripts/generate_mock_glb.py
Boxes in metres, right-handed +Y up, +Z forward; soles at Y=0, T-pose.
These are viewer fixtures, not body reconstruction, garment meshes, or draping.
"""

import json
import struct
from pathlib import Path

OUTPUT = Path(__file__).resolve().parents[1] / "backend" / "fixtures" / "assets"
BODY = [
    ("mock torso", [0, 1.18, 0], [.38, .56, .22], 0),
    ("mock head", [0, 1.60, 0], [.20, .24, .20], 0),
    ("mock left leg", [.105, .45, 0], [.16, .90, .18], 0),
    ("mock right leg", [-.105, .45, 0], [.16, .90, .18], 0),
    ("mock left arm", [.49, 1.36, 0], [.60, .14, .14], 0),
    ("mock right arm", [-.49, 1.36, 0], [.60, .14, .14], 0),
]
SHIRT = [
    ("mock shirt torso", [0, 1.17, 0], [.43, .59, .27], 1),
    ("mock left sleeve", [.30, 1.36, 0], [.24, .20, .22], 1),
    ("mock right sleeve", [-.30, 1.36, 0], [.24, .20, .22], 1),
]


def build_glb(boxes: list) -> bytes:
    vertices = [(-.5, -.5, -.5), (.5, -.5, -.5), (.5, .5, -.5), (-.5, .5, -.5),
                (-.5, -.5, .5), (.5, -.5, .5), (.5, .5, .5), (-.5, .5, .5)]
    indices = [0, 2, 1, 0, 3, 2, 4, 5, 6, 4, 6, 7, 0, 1, 5, 0, 5, 4,
               3, 7, 6, 3, 6, 2, 0, 4, 7, 0, 7, 3, 1, 2, 6, 1, 6, 5]
    positions = struct.pack("<24f", *(value for vertex in vertices for value in vertex))
    binary = positions + struct.pack("<36H", *indices)
    document = {
        "asset": {"version": "2.0", "generator": "M3 synthetic box fixture (NOT AI)"},
        "scene": 0, "scenes": [{"nodes": list(range(len(boxes)))}],
        "nodes": [{"name": name, "translation": center, "scale": size, "mesh": material}
                  for name, center, size, material in boxes],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1,
                                    "material": material}]} for material in range(2)],
        "materials": [{"name": name, "doubleSided": True, "pbrMetallicRoughness": {
            "baseColorFactor": color, "metallicFactor": 0, "roughnessFactor": 1,
        }} for name, color in [("mock body", [.65, .68, .72, 1]), ("mock shirt", [.1, .55, .9, 1])]],
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": len(positions), "target": 34962},
                        {"buffer": 0, "byteOffset": len(positions), "byteLength": 72, "target": 34963}],
        "accessors": [{"bufferView": 0, "componentType": 5126, "count": 8, "type": "VEC3",
                       "min": [-.5, -.5, -.5], "max": [.5, .5, .5]},
                      {"bufferView": 1, "componentType": 5123, "count": 36, "type": "SCALAR"}],
        "extras": {"source": "mock", "units": "m", "pose": "T", "up": "+Y", "forward": "+Z",
                   "note": "Fixed boxes; not scaled to measurements or garment size."},
    }
    encoded = json.dumps(document, separators=(",", ":"), sort_keys=True).encode("utf-8")
    encoded += b" " * (-len(encoded) % 4)
    binary += b"\0" * (-len(binary) % 4)
    total = 12 + 8 + len(encoded) + 8 + len(binary)
    return (struct.pack("<4sII", b"glTF", 2, total)
            + struct.pack("<I4s", len(encoded), b"JSON") + encoded
            + struct.pack("<I4s", len(binary), b"BIN\0") + binary)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, boxes in [("mock-body.glb", BODY), ("mock-tshirt.glb", SHIRT), ("mock-tryon.glb", BODY + SHIRT)]:
        path = OUTPUT / name
        path.write_bytes(build_glb(boxes))
        print(f"Generated {path.name}: {path.stat().st_size} bytes")
