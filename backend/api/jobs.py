from typing import Annotated

from fastapi import APIRouter, Depends

from backend.api.dependencies import get_orchestrator
from backend.schemas.common import SuccessResponse
from backend.schemas.job import JobSchema
from backend.services.orchestrator import TryOnOrchestrator

router = APIRouter(prefix='/jobs', tags=['jobs'])


@router.get("/{job_id}", response_model=SuccessResponse[JobSchema])
def get_job(
    job_id: str, service: Annotated[TryOnOrchestrator, Depends(get_orchestrator)],
) -> SuccessResponse[JobSchema]:
    return SuccessResponse(data=service.jobs.get(job_id))
