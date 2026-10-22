"""Wire contract for a body MPFB and one or more image-derived garments."""

from typing import Literal

from pydantic import Field, model_validator

from backend.schemas.common import AssetSchema, ContractModel, ErrorSchema, Provenance

GarmentType = Literal["tshirt", "shirt", "jacket", "pants", "skirt", "dress"]
GarmentSlot = Literal["upper", "lower", "onepiece"]


class GarmentMeasurementsCm(ContractModel):
    chest_circumference_cm: float | None = Field(default=None, ge=40, le=200)
    waist_circumference_cm: float | None = Field(default=None, ge=35, le=180)
    hip_circumference_cm: float | None = Field(default=None, ge=40, le=220)
    hem_circumference_cm: float | None = Field(default=None, ge=35, le=240)


class ImageTryOnGarment(ContractModel):
    slot: GarmentSlot
    garment_type: GarmentType
    reference_measurement: Literal["garment_length"] = "garment_length"
    reference_value_cm: float = Field(ge=1, le=300)
    fit_mode: Literal["auto", "measurements"] = "auto"
    ease_cm: float = Field(default=4, ge=0, le=20)
    garment_measurements_cm: GarmentMeasurementsCm | None = None

    @model_validator(mode="after")
    def validate_slot(self) -> "ImageTryOnGarment":
        valid_types = {
            "upper": {"tshirt", "shirt", "jacket"},
            "lower": {"pants", "skirt"},
            "onepiece": {"dress"},
        }
        if self.garment_type not in valid_types[self.slot]:
            raise ValueError("Garment type does not match outfit slot")
        measurements = self.garment_measurements_cm
        if self.fit_mode == "measurements":
            required = {
                "upper": ("chest_circumference_cm",),
                "lower": ("waist_circumference_cm", "hip_circumference_cm"),
                "onepiece": ("chest_circumference_cm", "waist_circumference_cm"),
            }[self.slot]
            if measurements is None or any(getattr(measurements, key) is None for key in required):
                raise ValueError("Required garment measurements are missing for this outfit slot")
            allowed = {
                "upper": {"chest_circumference_cm", "waist_circumference_cm", "hem_circumference_cm"},
                "lower": {"waist_circumference_cm", "hip_circumference_cm"},
                "onepiece": {"chest_circumference_cm", "waist_circumference_cm", "hem_circumference_cm"},
            }[self.slot]
            supplied = {
                key for key in measurements.model_fields_set
                if getattr(measurements, key) is not None
            }
            if supplied - allowed:
                raise ValueError("Garment measurement does not match outfit slot")
        elif measurements is not None:
            raise ValueError("Garment measurements require fit_mode='measurements'")
        return self


class ImageTryOnRequest(ContractModel):
    body_id: str = Field(min_length=1, max_length=100)
    garments: list[ImageTryOnGarment] = Field(default_factory=list, max_length=2)
    # Kept for stored jobs and clients using the original single-garment contract.
    garment_type: GarmentType | None = None
    reference_measurement: Literal["garment_length"] = "garment_length"
    reference_value_cm: float | None = Field(default=None, ge=1, le=300)
    simulate_cloth: bool = False

    @model_validator(mode="after")
    def validate_garments(self) -> "ImageTryOnRequest":
        if not self.garments and self.garment_type is not None:
            garment_type = self.garment_type
            slot: GarmentSlot = (
                "upper" if garment_type in {"tshirt", "shirt", "jacket"}
                else "onepiece" if garment_type == "dress" else "lower"
            )
            self.garments = [ImageTryOnGarment(
                slot=slot, garment_type=garment_type,
                reference_value_cm=self.reference_value_cm or 70,
            )]
        if not self.garments:
            raise ValueError("At least one garment is required")
        slots = [garment.slot for garment in self.garments]
        if len(slots) != len(set(slots)):
            raise ValueError("Only one garment per outfit slot is allowed")
        if "onepiece" in slots and len(slots) != 1:
            raise ValueError("A one-piece garment cannot be combined with separate garments")
        if len(self.garments) == 1 and self.garment_type is None:
            self.garment_type = self.garments[0].garment_type
            self.reference_value_cm = self.garments[0].reference_value_cm
        return self


class ImageTryOnGarmentResult(ContractModel):
    slot: GarmentSlot
    garment_type: GarmentType
    reconstruction: dict = Field(default_factory=dict)


class ImageTryOnResult(Provenance):
    body_id: str
    garment_type: str
    garments: list[ImageTryOnGarmentResult] = Field(default_factory=list)
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
