from fastapi import APIRouter, Request
from fastapi.responses import FileResponse

from backend.services.assets import resolve_asset

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("/{asset_name:path}", response_class=FileResponse, responses={
    200: {"description": "Registered GLB fixture", "content": {"model/gltf-binary": {}}},
})
def get_asset(asset_name: str, request: Request) -> FileResponse:
    path = resolve_asset(request.app.state.settings.asset_dir, asset_name)
    return FileResponse(path, media_type="model/gltf-binary")
