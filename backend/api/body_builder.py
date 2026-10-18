"""Manual body visualization API, separate from photo analysis and fit scoring."""

from typing import Annotated, Literal

from fastapi import APIRouter, BackgroundTasks, Path
from fastapi.responses import FileResponse
from pydantic import Field

from backend.schemas.common import ContractModel, SuccessResponse
from backend.services.blender_body import body_jobs

router = APIRouter(prefix="/body-builder", tags=["body-builder"])


class Proportions(ContractModel):
    shoulder_width: float = Field(default=0.5, ge=0, le=1)
    waist: float = Field(default=0.5, ge=0, le=1)
    hips: float = Field(default=0.5, ge=0, le=1)
    chest: float = Field(default=0.5, ge=0, le=1)
    leg_length: float = Field(default=0.5, ge=0, le=1)
    arm_length: float = Field(default=0.5, ge=0, le=1)
    muscle_tone: float = Field(default=0.5, ge=0, le=1)
    belly: float = Field(default=0.5, ge=0, le=1)
    buttocks: float = Field(default=0.5, ge=0, le=1)


class BodyParameters(ContractModel):
    height_cm: float = Field(default=170, ge=140, le=210)
    weight_kg: float = Field(default=65, ge=35, le=150)
    age: int = Field(default=25, ge=10, le=80)
    gender: Literal["female", "neutral", "male"] = "neutral"
    skin_color: str = Field(default="#b8b8b8", pattern=r"^#[0-9a-fA-F]{6}$")
    proportions: Proportions = Field(default_factory=Proportions)


class ClothingParameters(ContractModel):
    body_job_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    garment_id: str = Field(pattern=r"^[a-z0-9_-]{1,64}$")
    category: Literal["t_shirt", "shirt", "dress", "jacket", "pants"]
    color_hex: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    size: Literal["XS", "S", "M", "L", "XL", "XXL"] = "M"


@router.post("/generate", status_code=202)
def generate(parameters: BodyParameters, background_tasks: BackgroundTasks) -> SuccessResponse[dict]:
    job = body_jobs.create("body", parameters.model_dump())
    background_tasks.add_task(body_jobs.run, job["job_id"], parameters.model_dump())
    return SuccessResponse(data=job)


@router.post("/clothing", status_code=202)
def clothing(parameters: ClothingParameters, background_tasks: BackgroundTasks) -> SuccessResponse[dict]:
    job = body_jobs.create("clothing", parameters.model_dump(), parameters.body_job_id)
    background_tasks.add_task(body_jobs.run, job["job_id"], parameters.model_dump())
    return SuccessResponse(data=job)


@router.get("/jobs/{job_id}")
def get_job(job_id: Annotated[str, Path(pattern=r"^[a-f0-9]{32}$")]) -> SuccessResponse[dict]:
    return SuccessResponse(data=body_jobs.get(job_id))


@router.get("/assets/{job_id}.glb", response_class=FileResponse)
def get_asset(job_id: Annotated[str, Path(pattern=r"^[a-f0-9]{32}$")]) -> FileResponse:
    return FileResponse(body_jobs.asset(job_id), media_type="model/gltf-binary",
                        filename=f"body-{job_id}.glb")
