"""Persisted job state; execution still uses in-process BackgroundTasks."""

import logging
from collections.abc import Callable
from uuid import uuid4

from backend.core.errors import AppException
from backend.db.repository import JobRepository
from backend.schemas.common import ErrorSchema, Source
from backend.schemas.fit import FitRequest, FitResultSchema
from backend.schemas.job import JobSchema

logger = logging.getLogger(__name__)


class JobManager:
    def __init__(self, repository: JobRepository) -> None:
        self.repository = repository

    def create(self, request: FitRequest, source: Source) -> JobSchema:
        job = JobSchema(
            job_id=f"job_{uuid4().hex}", source=source, method="in_process_job",
            notes=["Job state is persisted; execution uses in-process BackgroundTasks."],
            status="pending", request=request,
        )
        return self.repository.create(job)

    def get(self, job_id: str) -> JobSchema:
        job = self.repository.get(job_id)
        if job is None:
            raise AppException(404, "JOB_NOT_FOUND", "Job not found")
        return job

    def run(self, job_id: str, work: Callable[[], FitResultSchema]) -> None:
        job = self.get(job_id)
        if job.status != "pending":
            return
        running = JobSchema(**{**job.model_dump(), "status": "running"})
        if not self.repository.transition(job_id, "pending", running):
            return
        try:
            result = FitResultSchema.model_validate(work())
            changes = {"status": "completed", "source": result.source, "result": result, "error": None}
        except Exception:
            logger.exception("Fit job %s failed", job_id)
            changes = {"status": "failed", "result": None, "error": ErrorSchema(
                code="PROCESSING_FAILED", message="Try-on processing failed",
            )}
        final = JobSchema(**{**job.model_dump(), **changes})
        self.repository.transition(job_id, "running", final)
