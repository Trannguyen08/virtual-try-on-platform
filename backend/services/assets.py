"""Only registered GLB fixtures can be served; never accept a filesystem path."""

from pathlib import Path

from backend.core.errors import AppException
from backend.schemas.common import AssetSchema

ASSET_NAMES = frozenset({"mock-body.glb", "mock-tshirt.glb", "mock-tryon.glb"})


def resolve_asset(root: Path, name: str) -> Path:
    if name not in ASSET_NAMES:
        raise AppException(404, "ASSET_NOT_FOUND", "Asset not found")
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise AppException(404, "ASSET_NOT_FOUND", "Asset not found")
    return path


def mock_asset(root: Path, name: str) -> AssetSchema | None:
    try:
        resolve_asset(root, name)
    except AppException:
        return None
    return AssetSchema(
        source="mock", method="box_geometry_fixture", url=f"/api/assets/{name}",
        notes=["Synthetic boxes for viewer integration only; not a reconstructed or draped mesh.",
               "Geometry is fixed and does not represent measurements or selected size."],
    )
