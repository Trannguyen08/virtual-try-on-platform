from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str
    retryable: bool = False


class CreateGenerationResponse(BaseModel):
    job_id: str
    generation_id: str
    input_mode: str
    received_views: list[str]
    status: str
    poll_url: str


class JobResponse(BaseModel):
    id: str
    generation_id: str
    status: str
    progress: int = Field(ge=0, le=100)
    provider: str
    created_at: datetime
    updated_at: datetime
    result_url: str | None = None
    error: ErrorDetail | None = None
    warnings: list[str] = Field(default_factory=list)


class AssetLinks(BaseModel):
    glb_url: str
    thumbnail_url: str | None = None


class GenerationResponse(BaseModel):
    id: str
    status: str
    input_mode: str
    views: list[str]
    assets: AssetLinks | None = None
    mesh: dict[str, Any] | None = None
    warnings: list[str] = Field(default_factory=list)
