"""Wire contract for a body MPFB and an image-derived garment scene."""

from typing import Literal

from pydantic import Field, model_validator

from backend.schemas.common import AssetSchema, ContractModel, ErrorSchema, Provenance


class ImageTryOnRequest(ContractModel):
    body_id: str = Field(min_length=1, max_length=100)
    garment_type: Literal["tshirt", "shirt", "jacket", "pants", "skirt", "dress"]
    reference_measurement: Literal["garment_length"] = "garment_length"
    reference_value_cm: float = Field(ge=1, le=300)
    simulate_cloth: bool = False


class ImageTryOnResult(Provenance):
    body_id: str
    garment_type: str
    tryon_mesh: AssetSchema
    simulation_ran: bool
    penetration_fraction: float = Field(ge=0, le=1)
    placement: str
    warnings: list[str] = Field(default_factory=list)
    reconstruction: dict = Field(default_factory=dict)


class ImageTryOnJob(ContractModel):
    job_id: str
    status: Literal["pending", "running", "completed", "failed"]
    request: ImageTryOnRequest
    result: ImageTryOnResult | None = None
    error: ErrorSchema | None = None
    attempt_count: int = 0

    @model_validator(mode="after")
    def validate_state(self) -> "ImageTryOnJob":
        if self.status == "completed":
            valid = self.result is not None and self.error is None
        elif self.status == "failed":
            valid = self.result is None and self.error is not None
        else:
            valid = self.result is None and self.error is None
        if not valid:
            raise ValueError("Job result/error must match status")
        return self
