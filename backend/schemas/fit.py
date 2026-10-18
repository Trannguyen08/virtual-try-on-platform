from typing import Literal

from pydantic import Field

from backend.schemas.common import ContractModel, Provenance, Size
from backend.schemas.predictor import PredictorSchema
from backend.schemas.simulation import SimulationSchema
from backend.schemas.size import SizeRecommendationSchema


class FitRequest(ContractModel):
    body_id: str = Field(min_length=1, max_length=100)
    garment_id: str = Field(min_length=1, max_length=100)
    size: Size


class RegionFitSchema(PredictorSchema):
    region: Literal["chest", "waist", "hip", "shoulder"]


class FitResultSchema(Provenance):
    body_id: str
    garment_id: str
    size: Size
    recommendation: SizeRecommendationSchema
    overall: PredictorSchema
    regions: list[RegionFitSchema]
    assets: SimulationSchema
