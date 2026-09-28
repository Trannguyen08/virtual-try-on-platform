"""Process-local job store. A restart discards everything; use one worker."""

import logging
from collections.abc import Callable
from threading import RLock
from uuid import uuid4

from backend.core.errors import AppException
from backend.schemas.common import ErrorSchema, Source
from backend.schemas.fit import FitRequest, FitResultSchema
from backend.schemas.job import JobSchema

logger = logging.getLogger(__name__)


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, JobSchema] = {}
        self._lock = RLock()

    def create(self, request: FitRequest, source: Source) -> JobSchema:
        job = JobSchema(
            job_id=f"job_{uuid4().hex}", source=source, method="in_process_job",
            notes=["In-memory job; discarded on server restart."], status="pending", request=request,
        )
        with self._lock:
            self._jobs[job.job_id] = job.model_copy(deep=True)
        return job

    def get(self, job_id: str) -> JobSchema:
        with self._lock:
            if job_id not in self._jobs:
                raise AppException(404, "JOB_NOT_FOUND", "Job not found")
            return self._jobs[job_id].model_copy(deep=True)

    def run(self, job_id: str, work: Callable[[], FitResultSchema]) -> None:
        with self._lock:
            job = self.get(job_id)
            if job.status != "pending":
                return
            self._jobs[job_id] = JobSchema(**{**job.model_dump(), "status": "running"})
        try:
            result = FitResultSchema.model_validate(work())
            changes = {"status": "completed", "source": result.source, "result": result, "error": None}
        except Exception:
            logger.exception("Fit job %s failed", job_id)
            changes = {"status": "failed", "result": None, "error": ErrorSchema(
                code="PROCESSING_FAILED", message="Try-on processing failed",
            )}
        with self._lock:
            self._jobs[job_id] = JobSchema(**{**job.model_dump(), **changes})
