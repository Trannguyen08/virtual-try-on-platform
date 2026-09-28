"""Shared wire types; real adapters use the same schema as mock providers."""

from typing import Annotated, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

Source = Literal["mock", "module", "mixed"]
Size = Literal["S", "M", "L", "XL"]
Confidence = Annotated[float, Field(ge=0, le=1)] | None
Score = Annotated[float, Field(ge=0, le=100)] | None


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Provenance(ContractModel):
    source: Source
    method: str
    notes: list[str]


class AssetSchema(Provenance):
    format: Literal["glb"] = "glb"
    url: str = Field(pattern=r"^/api/assets/[a-zA-Z0-9_-]+\.glb$")


class ErrorDetail(ContractModel):
    field: str
    message: str


class ErrorSchema(ContractModel):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)


T = TypeVar("T")


class SuccessResponse(ContractModel, Generic[T]):
    data: T
    error: None = None


class ErrorResponse(ContractModel):
    data: None = None
    error: ErrorSchema
