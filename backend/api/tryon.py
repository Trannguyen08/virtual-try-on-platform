from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile

from backend.api.dependencies import get_orchestrator
from backend.schemas.body import BodySchema
from backend.schemas.common import SuccessResponse
from backend.schemas.fit import FitRequest
from backend.schemas.job import JobSchema
from backend.services.orchestrator import TryOnOrchestrator

router = APIRouter(prefix='/tryon', tags=['tryon'])


@router.post("/analyze", response_model=SuccessResponse[BodySchema])
async def analyze(
    image: Annotated[UploadFile, File(description="PNG/JPEG, max 5 MiB; mock does not measure from image")],
    height_cm: Annotated[float, Form(ge=140, le=210, allow_inf_nan=False)],
    service: Annotated[TryOnOrchestrator, Depends(get_orchestrator)],
) -> SuccessResponse[BodySchema]:
    return SuccessResponse(data=await service.analyze(image, height_cm))


@router.post("/fit", status_code=202, response_model=SuccessResponse[JobSchema])
def fit(
    request: FitRequest, background_tasks: BackgroundTasks,
    service: Annotated[TryOnOrchestrator, Depends(get_orchestrator)],
) -> SuccessResponse[JobSchema]:
    body, garment = service.fit_inputs(request)
    job = service.jobs.create(request, service.provider.source)
    background_tasks.add_task(
        service.jobs.run, job.job_id, lambda: service.provider.fit(body, garment, request),
    )
    return SuccessResponse(data=job)
