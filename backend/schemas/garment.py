from typing import Literal

from pydantic import Field

from backend.schemas.common import AssetSchema, ContractModel, Provenance, Size


class GarmentSizeSchema(ContractModel):
    size: Size
    chest_cm: float = Field(gt=0)
    waist_cm: float = Field(gt=0)
    hem_cm: float = Field(gt=0)
    shoulder_width_cm: float = Field(gt=0)
    length_cm: float = Field(gt=0)


class GarmentSchema(Provenance):
    garment_id: str
    name: str
    category: Literal["t_shirt"]
    sizes: list[GarmentSizeSchema]
    mesh: AssetSchema | None
