from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class JobStatus(str, Enum):
    VALIDATING = "validating"
    UPLOADING = "uploading"
    QUEUED = "queued"
    GENERATING = "generating"
    DOWNLOADING = "downloading"
    POSTPROCESSING = "postprocessing"
    VALIDATING_MESH = "validating_mesh"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


TERMINAL_STATUSES = {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED}


ALLOWED_TRANSITIONS = {
    JobStatus.VALIDATING: {JobStatus.UPLOADING, JobStatus.FAILED},
    JobStatus.UPLOADING: {JobStatus.QUEUED, JobStatus.FAILED},
    JobStatus.QUEUED: {
        JobStatus.GENERATING,
        JobStatus.DOWNLOADING,
        JobStatus.FAILED,
        JobStatus.CANCELLED,
    },
    JobStatus.GENERATING: {
        JobStatus.GENERATING,
        JobStatus.DOWNLOADING,
        JobStatus.FAILED,
        JobStatus.CANCELLED,
    },
    JobStatus.DOWNLOADING: {JobStatus.POSTPROCESSING, JobStatus.FAILED},
    JobStatus.POSTPROCESSING: {JobStatus.VALIDATING_MESH, JobStatus.FAILED},
    JobStatus.VALIDATING_MESH: {JobStatus.COMPLETED, JobStatus.FAILED},
    JobStatus.COMPLETED: set(),
    JobStatus.FAILED: set(),
    JobStatus.CANCELLED: set(),
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class JobRecord:
    id: str
    generation_id: str
    status: JobStatus
    progress: int
    provider: str
    preset: str
    views: tuple[str, ...]
    provider_task_id: str | None
    artifact_path: str | None
    thumbnail_path: str | None
    mesh_metadata: dict[str, Any] | None
    warnings: tuple[str, ...]
    error_code: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    last_polled_at: datetime | None

    def transition(self, status: JobStatus, **changes: Any) -> JobRecord:
        if status != self.status and status not in ALLOWED_TRANSITIONS[self.status]:
            raise ValueError(
                f"Invalid job transition: {self.status.value} -> {status.value}"
            )
        return replace(self, status=status, updated_at=utc_now(), **changes)
