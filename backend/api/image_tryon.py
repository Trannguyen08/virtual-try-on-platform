"""Image garment try-on routes, separate from the legacy mock fit contract."""

import json
from typing import Annotated, Literal

from fastapi import APIRouter, File, Form, Request, UploadFile

from backend.schemas.common import SuccessResponse
from backend.core.errors import AppException
from backend.schemas.image_tryon import ImageTryOnGarment, ImageTryOnJob, ImageTryOnRequest

router = APIRouter(prefix="/tryon/image-jobs", tags=["image-tryon"])


@router.post("", status_code=202, response_model=SuccessResponse[ImageTryOnJob])
async def create_image_tryon(
    request: Request,
    body_id: Annotated[str, Form(min_length=1, max_length=100)],
    front: Annotated[UploadFile | None, File()] = None,
    reference_value_cm: Annotated[float | None, Form(ge=1, le=300, allow_inf_nan=False)] = None,
    garment_type: Annotated[
        Literal["tshirt", "shirt", "jacket", "pants", "skirt", "dress"], Form()
    ] = "tshirt",
    simulate_cloth: Annotated[bool, Form()] = False,
    back: Annotated[UploadFile | None, File()] = None,
    garments_json: Annotated[str | None, Form()] = None,
    garment_0_front: Annotated[UploadFile | None, File()] = None,
    garment_0_back: Annotated[UploadFile | None, File()] = None,
    garment_1_front: Annotated[UploadFile | None, File()] = None,
    garment_1_back: Annotated[UploadFile | None, File()] = None,
) -> SuccessResponse[ImageTryOnJob]:
    if garments_json:
        try:
            garment_data = json.loads(garments_json)
            garments = [ImageTryOnGarment.model_validate(item) for item in garment_data]
        except (TypeError, ValueError) as exc:
            raise AppException(422, "INVALID_GARMENT_LIST", "Garment list is invalid") from exc
        body_request = ImageTryOnRequest(
            body_id=body_id, garments=garments, simulate_cloth=simulate_cloth,
        )
        uploads = {
            "0_front": garment_0_front, "0_back": garment_0_back,
            "1_front": garment_1_front, "1_back": garment_1_back,
        }
    else:
        if front is None:
            raise AppException(422, "FRONT_VIEW_REQUIRED", "Front garment image is required")
        body_request = ImageTryOnRequest(
            body_id=body_id, garment_type=garment_type,
            reference_value_cm=reference_value_cm or 70,
            simulate_cloth=simulate_cloth,
        )
        uploads = {"0_front": front, "0_back": back}
    job = await request.app.state.image_tryon.submit(body_request, uploads)
    return SuccessResponse(data=job)


@router.get("/{job_id}", response_model=SuccessResponse[ImageTryOnJob])
def get_image_tryon(job_id: str, request: Request) -> SuccessResponse[ImageTryOnJob]:
    return SuccessResponse(data=request.app.state.image_tryon.get(job_id))
