from __future__ import annotations

import asyncio
import uuid
from collections.abc import Mapping
from dataclasses import asdict
from datetime import timedelta
from pathlib import Path

from garment.reconstruction.config import get_preset
from garment.reconstruction.contracts import (
    Garment3DProvider,
    GarmentView,
    GenerationRequest,
    MeshPostProcessor,
    TaskState,
)
from garment.reconstruction.errors import ReconstructionError
from garment.reconstruction.preprocessing import ImagePreprocessor
from garment.reconstruction.validation import GlbValidator

from .models import TERMINAL_STATUSES, JobRecord, JobStatus, utc_now
from .repository import JobRepository


class Garment3DService:
    def __init__(
        self,
        *,
        repository: JobRepository,
        provider: Garment3DProvider,
        preprocessor: ImagePreprocessor,
        validator: GlbValidator,
        postprocessor: MeshPostProcessor,
        output_dir: Path,
        preset: str,
        max_artifact_bytes: int,
        poll_cache_seconds: int,
    ) -> None:
        self.repository = repository
        self.provider = provider
        self.preprocessor = preprocessor
        self.validator = validator
        self.postprocessor = postprocessor
        self.output_dir = output_dir
        self.preset = preset
        self.max_artifact_bytes = max_artifact_bytes
        self.poll_cache_seconds = poll_cache_seconds
        self._locks: dict[str, asyncio.Lock] = {}

    async def submit(self, sources: Mapping[GarmentView, Path]) -> JobRecord:
        job_id = f"job_{uuid.uuid4().hex}"
        generation_id = f"gen_{uuid.uuid4().hex}"
        now = utc_now()
        record = JobRecord(
            id=job_id,
            generation_id=generation_id,
            status=JobStatus.VALIDATING,
            progress=0,
            provider=self.provider.name,
            preset=self.preset,
            views=tuple(view.value for view in sources),
            provider_task_id=None,
            artifact_path=None,
            thumbnail_path=None,
            mesh_metadata=None,
            warnings=(),
            error_code=None,
            error_message=None,
            created_at=now,
            updated_at=now,
            last_polled_at=None,
        )
        self.repository.create(record)
        generation_dir = self.output_dir / generation_id

        try:
            images = await asyncio.to_thread(
                self.preprocessor.process,
                sources,
                generation_dir / "normalized",
            )
            warnings = tuple(warning for image in images for warning in image.warnings)
            if len(images) == 1:
                warnings += ("BACK_AND_SIDES_INFERRED_FROM_SINGLE_IMAGE",)
            record = record.transition(
                JobStatus.UPLOADING, progress=5, warnings=warnings
            )
            self.repository.save(record)

            request = GenerationRequest(
                images=images,
                options=get_preset(self.preset).to_options(seed=0),
            )
            task = await self.provider.create_task(request)
            record = record.transition(
                JobStatus.QUEUED,
                progress=10,
                provider_task_id=task.external_id,
            )
            self.repository.save(record)
            return record
        except ReconstructionError as exc:
            failed = record.transition(
                JobStatus.FAILED,
                error_code=exc.code,
                error_message=exc.message,
            )
            self.repository.save(failed)
            raise
        except Exception:
            failed = record.transition(
                JobStatus.FAILED,
                error_code="INTERNAL_ERROR",
                error_message="Could not create the garment 3D task",
            )
            self.repository.save(failed)
            raise

    async def refresh(self, job_id: str, *, force: bool = False) -> JobRecord | None:
        record = self.repository.get(job_id)
        if record is None or record.status in TERMINAL_STATUSES:
            return record
        lock = self._locks.setdefault(job_id, asyncio.Lock())
        async with lock:
            record = self.repository.get(job_id)
            if record is None or record.status in TERMINAL_STATUSES:
                return record
            if not force and record.last_polled_at:
                age = utc_now() - record.last_polled_at
                if age < timedelta(seconds=self.poll_cache_seconds):
                    return record
            if not record.provider_task_id:
                return self._fail(
                    record, "INVALID_JOB_STATE", "Job is missing its provider task ID"
                )
            try:
                snapshot = await self.provider.get_task(record.provider_task_id)
                polled_at = utc_now()
                if snapshot.state is TaskState.QUEUED:
                    record = record.transition(
                        JobStatus.QUEUED,
                        progress=max(record.progress, snapshot.progress),
                        last_polled_at=polled_at,
                    )
                elif snapshot.state is TaskState.RUNNING:
                    record = record.transition(
                        JobStatus.GENERATING,
                        progress=max(10, snapshot.progress),
                        last_polled_at=polled_at,
                    )
                elif snapshot.state is TaskState.FAILED:
                    record = self._fail(
                        record,
                        snapshot.error_code or "PROVIDER_TASK_FAILED",
                        snapshot.error_message
                        or "3D provider could not generate the model",
                    )
                elif snapshot.state is TaskState.CANCELLED:
                    record = record.transition(
                        JobStatus.CANCELLED, last_polled_at=polled_at
                    )
                elif snapshot.state is TaskState.SUCCESS and snapshot.result:
                    record = await self._materialize(
                        record, snapshot.result.model_url, snapshot.result.thumbnail_url
                    )
                else:
                    record = self._fail(
                        record,
                        "PROVIDER_INVALID_RESPONSE",
                        "Provider returned no result",
                    )
                self.repository.save(record)
                return record
            except ReconstructionError as exc:
                failed = self._fail(record, exc.code, exc.message)
                self.repository.save(failed)
                return failed

    async def _materialize(
        self,
        record: JobRecord,
        model_url: str,
        thumbnail_url: str | None,
    ) -> JobRecord:
        generation_dir = self.output_dir / record.generation_id
        source = generation_dir / "source.glb"
        model = generation_dir / "model.glb"
        if record.status in {JobStatus.QUEUED, JobStatus.GENERATING}:
            record = record.transition(
                JobStatus.DOWNLOADING, progress=90, last_polled_at=utc_now()
            )
            self.repository.save(record)
        if not source.is_file():
            if record.status is not JobStatus.DOWNLOADING:
                raise ReconstructionError(
                    "ARTIFACT_RECOVERY_FAILED",
                    "Generated source artifact is missing during recovery",
                    http_status=500,
                )
            await self.provider.download(model_url, source, self.max_artifact_bytes)

        if record.status is JobStatus.DOWNLOADING:
            record = record.transition(JobStatus.POSTPROCESSING, progress=94)
            self.repository.save(record)
        if not model.is_file():
            if record.status is not JobStatus.POSTPROCESSING:
                raise ReconstructionError(
                    "ARTIFACT_RECOVERY_FAILED",
                    "Processed artifact is missing during recovery",
                    http_status=500,
                )
            target_faces = get_preset(record.preset).target_face_count
            await asyncio.to_thread(
                self.postprocessor.process, source, model, target_faces
            )

        if record.status is JobStatus.POSTPROCESSING:
            record = record.transition(JobStatus.VALIDATING_MESH, progress=98)
            self.repository.save(record)
        metadata = await asyncio.to_thread(self.validator.validate, model)

        thumbnail_path = None
        if thumbnail_url:
            thumbnail = generation_dir / "thumbnail.png"
            try:
                await self.provider.download(thumbnail_url, thumbnail, 10 * 1024 * 1024)
                thumbnail_path = str(thumbnail)
            except ReconstructionError:
                thumbnail.unlink(missing_ok=True)

        return record.transition(
            JobStatus.COMPLETED,
            progress=100,
            artifact_path=str(model),
            thumbnail_path=thumbnail_path,
            mesh_metadata=asdict(metadata),
            last_polled_at=utc_now(),
        )

    def get_by_generation(self, generation_id: str) -> JobRecord | None:
        return self.repository.get_by_generation(generation_id)

    def artifact(self, generation_id: str, kind: str) -> Path | None:
        record = self.get_by_generation(generation_id)
        if not record or record.status is not JobStatus.COMPLETED:
            return None
        value = record.artifact_path if kind == "model" else record.thumbnail_path
        if not value:
            return None
        path = Path(value).resolve()
        expected_root = (self.output_dir / generation_id).resolve()
        if expected_root not in path.parents or not path.is_file():
            return None
        return path

    @staticmethod
    def _fail(record: JobRecord, code: str, message: str) -> JobRecord:
        return record.transition(
            JobStatus.FAILED,
            error_code=code,
            error_message=message,
            last_polled_at=utc_now(),
        )
