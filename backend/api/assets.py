from fastapi import APIRouter, Request
from fastapi.responses import FileResponse


router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("/{asset_name:path}", response_class=FileResponse, responses={
    200: {"description": "Registered GLB fixture", "content": {"model/gltf-binary": {}}},
})
def get_asset(asset_name: str, request: Request) -> FileResponse:
    path = request.app.state.storage.asset_path(asset_name)
    return FileResponse(path, media_type="model/gltf-binary")
