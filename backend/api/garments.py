from typing import Annotated

from fastapi import APIRouter, Depends

from backend.api.dependencies import get_orchestrator
from backend.schemas.common import SuccessResponse
from backend.schemas.garment import GarmentSchema
from backend.services.orchestrator import TryOnOrchestrator

router = APIRouter(prefix='/garments', tags=['garments'])


@router.get("", response_model=SuccessResponse[list[GarmentSchema]])
def list_garments(
    service: Annotated[TryOnOrchestrator, Depends(get_orchestrator)],
) -> SuccessResponse[list[GarmentSchema]]:
    return SuccessResponse(data=service.provider.garments())
