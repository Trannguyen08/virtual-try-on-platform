from __future__ import annotations

import asyncio
import json
import logging
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

from ..contracts import (
    GenerationRequest,
    ProviderResult,
    ProviderTask,
    ProviderTaskStatus,
    TaskState,
)
from ..errors import ReconstructionError
from ..local_pipeline import LocalGarmentReconstructor

logger = logging.getLogger(__name__)


@dataclass
class _LocalTaskState:
    state: TaskState = TaskState.QUEUED
    progress: int = 0
    result: ProviderResult | None = None
    error_code: str | None = None
    error_message: str | None = None


class LocalGarment3DProvider:
    """Self-hosted provider that never uploads user images to a third party."""

    name = "local"

    def __init__(
        self,
        output_dir: Path,
        reconstructor: LocalGarmentReconstructor | None = None,
    ) -> None:
        self.output_dir = output_dir
        self.reconstructor = reconstructor or LocalGarmentReconstructor()
        self._tasks: dict[str, _LocalTaskState] = {}
        self._workers: dict[str, asyncio.Task[None]] = {}

    async def create_task(self, request: GenerationRequest) -> ProviderTask:
        external_id = f"local_{uuid.uuid4().hex}"
        self._tasks[external_id] = _LocalTaskState()
        self._workers[external_id] = asyncio.create_task(
            self._generate(external_id, request)
        )
        return ProviderTask(provider=self.name, external_id=external_id)

    async def _generate(self, external_id: str, request: GenerationRequest) -> None:
        state = self._tasks[external_id]
        state.state = TaskState.RUNNING
        state.progress = 25
        try:
            result = await asyncio.to_thread(
                self.reconstructor.reconstruct,
                request,
                self.output_dir / external_id,
                lambda progress: setattr(state, "progress", progress),
            )
            state.result = ProviderResult(
                model_url=result.model_path.as_uri(),
                thumbnail_url=result.preview_path.as_uri(),
                metadata=result.metadata,
            )
            state.progress = 100
            state.state = TaskState.SUCCESS
        except ReconstructionError as exc:
            state.state = TaskState.FAILED
            state.progress = 100
            state.error_code = exc.code
            state.error_message = exc.message
        except Exception:
            logger.exception("Local garment reconstruction crashed (%s)", external_id)
            state.state = TaskState.FAILED
            state.progress = 100
            state.error_code = "LOCAL_RECONSTRUCTION_FAILED"
            state.error_message = "Local garment reconstruction failed"

    async def get_task(self, external_id: str) -> ProviderTaskStatus:
        state = self._tasks.get(external_id)
        if state is None:
            task_dir = self.output_dir / external_id
            model_path = task_dir / "model.glb"
            metadata_path = task_dir / "garment-metadata.json"
            preview_path = task_dir / "preview.png"
            if model_path.is_file() and metadata_path.is_file():
                try:
                    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    metadata = {}
                return ProviderTaskStatus(
                    state=TaskState.SUCCESS,
                    progress=100,
                    result=ProviderResult(
                        model_url=model_path.as_uri(),
                        thumbnail_url=(
                            preview_path.as_uri() if preview_path.is_file() else None
                        ),
                        metadata=metadata,
                    ),
                )
            return ProviderTaskStatus(
                state=TaskState.FAILED,
                progress=100,
                error_code="PROVIDER_TASK_NOT_FOUND",
                error_message="Local reconstruction task was not found",
            )
        return ProviderTaskStatus(
            state=state.state,
            progress=state.progress,
            result=state.result,
            error_code=state.error_code,
            error_message=state.error_message,
        )

    async def download(self, url: str, destination: Path, max_bytes: int) -> None:
        parsed = urlparse(url)
        source = (
            Path(url2pathname(unquote(parsed.path)))
            if parsed.scheme == "file"
            else Path(url)
        )
        if not source.is_file():
            raise ReconstructionError(
                "LOCAL_ARTIFACT_MISSING", "Local reconstruction artifact is missing"
            )
        if source.stat().st_size > max_bytes:
            raise ReconstructionError(
                "LOCAL_ARTIFACT_TOO_LARGE", "Local reconstruction artifact is too large"
            )
        destination.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(shutil.copyfile, source, destination)

    async def cancel_task(self, external_id: str) -> bool:
        worker = self._workers.get(external_id)
        if worker is None or worker.done():
            return False
        worker.cancel()
        self._tasks[external_id].state = TaskState.CANCELLED
        return True

    async def close(self) -> None:
        active = [worker for worker in self._workers.values() if not worker.done()]
        for worker in active:
            worker.cancel()
        if active:
            await asyncio.gather(*active, return_exceptions=True)
