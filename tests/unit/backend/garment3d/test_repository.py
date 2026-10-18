from pathlib import Path

from backend.garment3d.models import JobRecord, JobStatus, utc_now
from backend.garment3d.repository import JobRepository


def test_repository_round_trip(tmp_path: Path) -> None:
    repository = JobRepository(tmp_path / "jobs.sqlite3")
    repository.initialize()
    now = utc_now()
    record = JobRecord(
        id="job_1",
        generation_id="gen_1",
        status=JobStatus.QUEUED,
        progress=10,
        provider="mock",
        preset="balanced",
        views=("front", "back"),
        provider_task_id="mock_1",
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

    repository.create(record)
    stored = repository.get("job_1")
    assert stored == record

    completed = stored.transition(JobStatus.DOWNLOADING, progress=90)
    repository.save(completed)
    assert repository.get_by_generation("gen_1").status is JobStatus.DOWNLOADING
