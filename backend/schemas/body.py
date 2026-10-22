from pydantic import Field

from backend.schemas.common import AssetSchema, Confidence, ContractModel, Provenance


class BodyMeasurementSchema(ContractModel):
    height_cm: float = Field(ge=140, le=210)
    chest_cm: float = Field(gt=0)
    waist_cm: float = Field(gt=0)
    hip_cm: float = Field(gt=0)
    shoulder_width_cm: float = Field(gt=0)


class BodySchema(Provenance):
    body_id: str
    measurements: BodyMeasurementSchema
    confidence: Confidence
    mesh: AssetSchema | None
