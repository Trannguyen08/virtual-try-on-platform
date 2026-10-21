"""Image garment try-on routes, separate from the legacy mock fit contract."""

from typing import Annotated, Literal

from fastapi import APIRouter, File, Form, Request, UploadFile

from backend.schemas.common import SuccessResponse
from backend.schemas.image_tryon import ImageTryOnJob, ImageTryOnRequest

router = APIRouter(prefix="/tryon/image-jobs", tags=["image-tryon"])


@router.post("", status_code=202, response_model=SuccessResponse[ImageTryOnJob])
async def create_image_tryon(
    request: Request,
    body_id: Annotated[str, Form(min_length=1, max_length=100)],
    front: Annotated[UploadFile, File()],
    reference_value_cm: Annotated[float, Form(ge=1, le=300, allow_inf_nan=False)],
    garment_type: Annotated[
        Literal["tshirt", "shirt", "jacket", "pants", "skirt", "dress"], Form()
    ] = "tshirt",
    simulate_cloth: Annotated[bool, Form()] = False,
    left: Annotated[UploadFile | None, File()] = None,
    back: Annotated[UploadFile | None, File()] = None,
    right: Annotated[UploadFile | None, File()] = None,
) -> SuccessResponse[ImageTryOnJob]:
    body_request = ImageTryOnRequest(
        body_id=body_id, garment_type=garment_type,
        reference_value_cm=reference_value_cm, simulate_cloth=simulate_cloth,
    )
    job = await request.app.state.image_tryon.submit(body_request, {
        "front": front, "left": left, "back": back, "right": right,
    })
    return SuccessResponse(data=job)


@router.get("/{job_id}", response_model=SuccessResponse[ImageTryOnJob])
def get_image_tryon(job_id: str, request: Request) -> SuccessResponse[ImageTryOnJob]:
    return SuccessResponse(data=request.app.state.image_tryon.get(job_id))
