from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from garment.reconstruction.contracts import (
    GarmentView,
    SUPPORTED_GARMENT_TYPES,
    SUPPORTED_REFERENCE_MEASUREMENTS,
)
from garment.reconstruction.errors import ReconstructionError

from .models import JobRecord, JobStatus
from .schemas import (
    AssetLinks,
    CreateGenerationResponse,
    ErrorDetail,
    GenerationResponse,
    JobResponse,
)
from .service import Garment3DService
from .uploads import save_upload

router = APIRouter(prefix="/garment3d", tags=["garment3d"])


def service_from(request: Request) -> Garment3DService:
    return request.app.state.garment3d_service


@router.post("/generations", response_model=CreateGenerationResponse, status_code=202)
async def create_generation(
    request: Request,
    front: Annotated[UploadFile, File()],
    left: Annotated[UploadFile | None, File()] = None,
    back: Annotated[UploadFile | None, File()] = None,
    right: Annotated[UploadFile | None, File()] = None,
    garment_type: Annotated[str, Form()] = "tshirt",
    reference_measurement: Annotated[str | None, Form()] = None,
    reference_value_cm: Annotated[float | None, Form()] = None,
) -> CreateGenerationResponse:
    settings = request.app.state.garment3d_settings
    uploads = {
        GarmentView.FRONT: front,
        GarmentView.LEFT: left,
        GarmentView.BACK: back,
        GarmentView.RIGHT: right,
    }
    temp_dir = Path(
        tempfile.mkdtemp(prefix="garment3d-upload-", dir=settings.output_dir)
    )
    sources: dict[GarmentView, Path] = {}
    try:
        garment_type = garment_type.lower().strip()
        if garment_type not in SUPPORTED_GARMENT_TYPES:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "UNSUPPORTED_GARMENT_TYPE",
                    "message": "Unsupported garment type",
                },
            )
        for view, upload in uploads.items():
            if upload is None:
                continue
            destination = temp_dir / f"{view.value}.upload"
            await save_upload(upload, destination, settings.max_upload_bytes)
            sources[view] = destination
        if (reference_measurement is None) != (reference_value_cm is None):
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INCOMPLETE_SCALE_REFERENCE",
                    "message": "Reference measurement and value must be provided together",
                },
            )
        if reference_measurement is not None:
            if reference_measurement not in SUPPORTED_REFERENCE_MEASUREMENTS:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "code": "UNSUPPORTED_REFERENCE_MEASUREMENT",
                        "message": "Unsupported scale reference measurement",
                    },
                )
            if reference_value_cm is None or not 1.0 <= reference_value_cm <= 300.0:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "code": "INVALID_REFERENCE_VALUE",
                        "message": "Reference value must be between 1 and 300 cm",
                    },
                )
        record = await service_from(request).submit(
            sources,
            garment_type=garment_type,
            reference_measurement=reference_measurement,
            reference_value_cm=reference_value_cm,
        )
    except ReconstructionError as exc:
        raise HTTPException(
            status_code=exc.http_status,
            detail={
                "code": exc.code,
                "message": exc.message,
                "retryable": exc.retryable,
            },
        ) from exc
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return CreateGenerationResponse(
        job_id=record.id,
        generation_id=record.generation_id,
        input_mode="multi_view" if len(record.views) > 1 else "single_view",
        received_views=list(record.views),
        status=record.status.value,
        poll_url=f"/garment3d/jobs/{record.id}",
    )


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(request: Request, job_id: str) -> JobResponse:
    record = await service_from(request).refresh(job_id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "JOB_NOT_FOUND", "message": "Job not found"},
        )
    return job_response(record)


@router.get("/generations/{generation_id}", response_model=GenerationResponse)
async def get_generation(request: Request, generation_id: str) -> GenerationResponse:
    service = service_from(request)
    record = service.get_by_generation(generation_id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "GENERATION_NOT_FOUND", "message": "Generation not found"},
        )
    assets = None
    if record.status is JobStatus.COMPLETED:
        assets = AssetLinks(
            glb_url=f"/garment3d/artifacts/{generation_id}/model.glb",
            thumbnail_url=(
                f"/garment3d/artifacts/{generation_id}/thumbnail.png"
                if record.thumbnail_path
                else None
            ),
            metadata_url=(
                f"/garment3d/artifacts/{generation_id}/garment-metadata.json"
                if record.mesh_metadata and record.mesh_metadata.get("garment")
                else None
            ),
        )
    return GenerationResponse(
        id=generation_id,
        status=record.status.value,
        input_mode="multi_view" if len(record.views) > 1 else "single_view",
        views=list(record.views),
        assets=assets,
        mesh=record.mesh_metadata,
        garment=(record.mesh_metadata or {}).get("garment"),
        warnings=list(record.warnings),
    )


@router.get("/artifacts/{generation_id}/model.glb", response_class=FileResponse)
async def get_model(request: Request, generation_id: str) -> FileResponse:
    path = service_from(request).artifact(generation_id, "model")
    if path is None:
        raise HTTPException(status_code=404, detail="Model artifact not found")
    return FileResponse(
        path, media_type="model/gltf-binary", filename=f"{generation_id}.glb"
    )


@router.get("/artifacts/{generation_id}/thumbnail.png", response_class=FileResponse)
async def get_thumbnail(request: Request, generation_id: str) -> FileResponse:
    path = service_from(request).artifact(generation_id, "thumbnail")
    if path is None:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(path, media_type="image/png", filename=f"{generation_id}.png")


@router.get(
    "/artifacts/{generation_id}/garment-metadata.json",
    response_class=FileResponse,
)
async def get_metadata(request: Request, generation_id: str) -> FileResponse:
    path = service_from(request).artifact(generation_id, "metadata")
    if path is None:
        raise HTTPException(status_code=404, detail="Garment metadata not found")
    return FileResponse(
        path,
        media_type="application/json",
        filename=f"{generation_id}-garment-metadata.json",
    )


def job_response(record: JobRecord) -> JobResponse:
    error = None
    if record.error_code:
        error = ErrorDetail(
            code=record.error_code,
            message=record.error_message or "Garment generation failed",
            retryable=record.error_code
            in {"PROVIDER_UNAVAILABLE", "PROVIDER_RATE_LIMITED"},
        )
    return JobResponse(
        id=record.id,
        generation_id=record.generation_id,
        status=record.status.value,
        progress=record.progress,
        provider=record.provider,
        created_at=record.created_at,
        updated_at=record.updated_at,
        result_url=(
            f"/garment3d/generations/{record.generation_id}"
            if record.status is JobStatus.COMPLETED
            else None
        ),
        error=error,
        warnings=list(record.warnings),
    )
