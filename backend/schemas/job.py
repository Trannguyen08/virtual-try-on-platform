from typing import Literal

from pydantic import model_validator

from backend.schemas.common import ErrorSchema, Provenance
from backend.schemas.fit import FitRequest, FitResultSchema


class JobSchema(Provenance):
    job_id: str
    status: Literal["pending", "running", "completed", "failed"]
    request: FitRequest
    result: FitResultSchema | None = None
    error: ErrorSchema | None = None

    @model_validator(mode="after")
    def validate_state(self) -> "JobSchema":
        if self.status == "completed":
            valid = self.result is not None and self.error is None
        elif self.status == "failed":
            valid = self.result is None and self.error is not None
        else:
            valid = self.result is None and self.error is None
        if not valid:
            raise ValueError("Job result/error must match its status")
        return self
