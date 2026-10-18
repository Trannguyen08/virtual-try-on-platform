"""Transactional CRUD for bodies, assets, jobs and processing steps."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.orm import sessionmaker

from backend.db.models import AssetRecord, BodyRecord, JobRecord, JobStepRecord, utc_now
from backend.schemas.body import BodySchema
from backend.schemas.job import JobSchema


class BodyRepository:
    def __init__(self, sessions: sessionmaker):
        self.sessions = sessions

    def create_mock(self, body: BodySchema) -> BodyRecord:
        with self.sessions.begin() as session:
            record = BodyRecord(
                body_id=body.body_id, kind="mock_analyzed", status="ready",
                source=body.source, method=body.method,
                schema_json=body.model_dump(mode="json"), metadata_json={},
            )
            session.add(record)
        return record

    def create_mpfb(self, body_id: str, *, status: str = "processing",
                    metadata: dict | None = None) -> BodyRecord:
        if status not in {"processing", "ready", "failed"}:
            raise ValueError("Invalid body status")
        with self.sessions.begin() as session:
            record = BodyRecord(body_id=body_id, kind="mpfb", status=status,
                                source="module", method="blender_mpfb",
                                schema_json=None, metadata_json=metadata or {})
            session.add(record)
        return record

    def get(self, body_id: str) -> BodyRecord | None:
        with self.sessions() as session:
            return session.get(BodyRecord, body_id)

    def list(self, *, kind: str | None = None, status: str | None = None) -> list[BodyRecord]:
        statement = select(BodyRecord)
        if kind is not None:
            statement = statement.where(BodyRecord.kind == kind)
        if status is not None:
            statement = statement.where(BodyRecord.status == status)
        with self.sessions() as session:
            return list(session.scalars(statement.order_by(BodyRecord.created_at)))

    def update_status(self, body_id: str, status: str, *, error_code: str | None = None) -> bool:
        if status not in {"processing", "ready", "failed"}:
            raise ValueError("Invalid body status")
        with self.sessions.begin() as session:
            result = session.execute(update(BodyRecord).where(BodyRecord.body_id == body_id).values(
                status=status, error_code=error_code, updated_at=utc_now(),
            ))
            return result.rowcount == 1


class AssetRepository:
    def __init__(self, sessions: sessionmaker):
        self.sessions = sessions

    def create(self, *, kind: str, scope: str, key: str, media_type: str,
               byte_size: int, sha256: str, public_name: str | None = None,
               body_id: str | None = None, job_id: str | None = None,
               metadata: dict | None = None) -> AssetRecord:
        with self.sessions.begin() as session:
            record = AssetRecord(
                asset_id=f"asset_{uuid4().hex}", kind=kind, status="available",
                storage_scope=scope, storage_key=key, public_name=public_name,
                media_type=media_type, byte_size=byte_size, sha256=sha256,
                body_id=body_id, job_id=job_id, metadata_json=metadata or {},
            )
            session.add(record)
        return record

    def get(self, asset_id: str) -> AssetRecord | None:
        with self.sessions() as session:
            return session.get(AssetRecord, asset_id)

    def get_by_public_name(self, name: str) -> AssetRecord | None:
        with self.sessions() as session:
            return session.scalar(select(AssetRecord).where(AssetRecord.public_name == name))

    def list(self, *, kind: str | None = None, body_id: str | None = None,
             job_id: str | None = None) -> list[AssetRecord]:
        statement = select(AssetRecord)
        if kind is not None:
            statement = statement.where(AssetRecord.kind == kind)
        if body_id is not None:
            statement = statement.where(AssetRecord.body_id == body_id)
        if job_id is not None:
            statement = statement.where(AssetRecord.job_id == job_id)
        with self.sessions() as session:
            return list(session.scalars(statement.order_by(AssetRecord.created_at)))

    def update_status(self, asset_id: str, status: str) -> bool:
        if status not in {"available", "missing", "failed"}:
            raise ValueError("Invalid asset status")
        with self.sessions.begin() as session:
            result = session.execute(update(AssetRecord).where(AssetRecord.asset_id == asset_id).values(
                status=status, updated_at=utc_now(),
            ))
            return result.rowcount == 1


class JobRepository:
    def __init__(self, sessions: sessionmaker):
        self.sessions = sessions

    @staticmethod
    def _schema(record: JobRecord) -> JobSchema:
        return JobSchema.model_validate({
            "job_id": record.job_id, "status": record.status,
            "source": record.source, "method": record.method, "notes": record.notes_json,
            "request": record.request_json, "result": record.result_json,
            "error": record.error_json,
        })

    def create(self, job: JobSchema) -> JobSchema:
        now = utc_now()
        with self.sessions.begin() as session:
            session.add(JobRecord(
                job_id=job.job_id, body_id=job.request.body_id,
                garment_id=job.request.garment_id, status=job.status,
                source=job.source, method=job.method, notes_json=job.notes,
                request_json=job.request.model_dump(mode="json"),
                result_json=None, error_json=None, created_at=now, updated_at=now,
            ))
            session.add(JobStepRecord(job_id=job.job_id, step="request_accepted", status="completed",
                                      started_at=now, finished_at=now, duration_ms=0, metadata_json={}))
            session.add(JobStepRecord(job_id=job.job_id, step="fit", status="pending",
                                      started_at=now, metadata_json={}))
        return job

    def get(self, job_id: str) -> JobSchema | None:
        with self.sessions() as session:
            record = session.get(JobRecord, job_id)
            return self._schema(record) if record else None

    def list(self, *, body_id: str | None = None, status: str | None = None) -> list[JobSchema]:
        statement = select(JobRecord)
        if body_id is not None:
            statement = statement.where(JobRecord.body_id == body_id)
        if status is not None:
            statement = statement.where(JobRecord.status == status)
        with self.sessions() as session:
            return [self._schema(row) for row in session.scalars(statement.order_by(JobRecord.created_at))]

    def transition(self, job_id: str, expected: str, updated: JobSchema) -> bool:
        now = utc_now()
        values = {
            "status": updated.status, "source": updated.source,
            "result_json": updated.result.model_dump(mode="json") if updated.result else None,
            "error_json": updated.error.model_dump(mode="json") if updated.error else None,
            "updated_at": now,
        }
        if updated.status == "running":
            values["started_at"] = now
        if updated.status in {"completed", "failed"}:
            values["finished_at"] = now
        with self.sessions.begin() as session:
            if updated.status in {"completed", "failed"}:
                started = session.scalar(select(JobRecord.started_at).where(JobRecord.job_id == job_id))
                if started is not None:
                    values["duration_ms"] = max(0, int((now - self._aware(started)).total_seconds() * 1000))
            result = session.execute(update(JobRecord).where(
                JobRecord.job_id == job_id, JobRecord.status == expected,
            ).values(**values))
            if result.rowcount != 1:
                return False
            step = session.scalar(select(JobStepRecord).where(
                JobStepRecord.job_id == job_id, JobStepRecord.step == "fit",
            ).order_by(JobStepRecord.id.desc()))
            if step is not None:
                if updated.status == "running":
                    step.status = "running"
                    step.started_at = now
                else:
                    step.status = updated.status
                    step.finished_at = now
                    step.duration_ms = max(0, int((now - self._aware(step.started_at)).total_seconds() * 1000))
                    step.error_code = updated.error.code if updated.error else None
                    step.message = updated.error.message if updated.error else None
        return True

    @staticmethod
    def _aware(value: datetime) -> datetime:
        return value if value.tzinfo else value.replace(tzinfo=utc_now().tzinfo)

    def steps(self, job_id: str) -> list[JobStepRecord]:
        with self.sessions() as session:
            return list(session.scalars(select(JobStepRecord).where(
                JobStepRecord.job_id == job_id,
            ).order_by(JobStepRecord.id)))

    def log_step(self, job_id: str, step: str, status: str, *,
                 error_code: str | None = None, message: str | None = None,
                 metadata: dict | None = None) -> JobStepRecord:
        if status not in {"pending", "running", "completed", "failed"}:
            raise ValueError("Invalid step status")
        now = utc_now()
        terminal = status in {"completed", "failed"}
        with self.sessions.begin() as session:
            record = JobStepRecord(
                job_id=job_id, step=step, status=status, error_code=error_code,
                message=message, started_at=now, finished_at=now if terminal else None,
                duration_ms=0 if terminal else None, metadata_json=metadata or {},
            )
            session.add(record)
        return record
