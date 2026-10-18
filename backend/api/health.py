from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix='/health', tags=['health'])


class HealthResponse(BaseModel):
    status: Literal["healthy"]


@router.get("", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="healthy")
