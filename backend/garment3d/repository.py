from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from .models import JobRecord, JobStatus


class JobRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS garment3d_jobs (
                    id TEXT PRIMARY KEY,
                    generation_id TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    progress INTEGER NOT NULL,
                    provider TEXT NOT NULL,
                    preset TEXT NOT NULL,
                    views_json TEXT NOT NULL,
                    provider_task_id TEXT,
                    artifact_path TEXT,
                    thumbnail_path TEXT,
                    mesh_metadata_json TEXT,
                    warnings_json TEXT NOT NULL,
                    error_code TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_polled_at TEXT
                )
                """
            )

    def create(self, record: JobRecord) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO garment3d_jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                self._serialize(record),
            )

    def save(self, record: JobRecord) -> None:
        values = self._serialize(record)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE garment3d_jobs SET
                    generation_id = ?, status = ?, progress = ?, provider = ?, preset = ?,
                    views_json = ?, provider_task_id = ?, artifact_path = ?, thumbnail_path = ?,
                    mesh_metadata_json = ?, warnings_json = ?, error_code = ?, error_message = ?,
                    created_at = ?, updated_at = ?, last_polled_at = ?
                WHERE id = ?
                """,
                values[1:] + values[:1],
            )
            if cursor.rowcount != 1:
                raise KeyError(record.id)

    def get(self, job_id: str) -> JobRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM garment3d_jobs WHERE id = ?",
                (job_id,),
            ).fetchone()
        return self._deserialize(row) if row else None

    def get_by_generation(self, generation_id: str) -> JobRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM garment3d_jobs WHERE generation_id = ?",
                (generation_id,),
            ).fetchone()
        return self._deserialize(row) if row else None

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _serialize(record: JobRecord) -> tuple:
        return (
            record.id,
            record.generation_id,
            record.status.value,
            record.progress,
            record.provider,
            record.preset,
            json.dumps(record.views),
            record.provider_task_id,
            record.artifact_path,
            record.thumbnail_path,
            json.dumps(record.mesh_metadata)
            if record.mesh_metadata is not None
            else None,
            json.dumps(record.warnings),
            record.error_code,
            record.error_message,
            record.created_at.isoformat(),
            record.updated_at.isoformat(),
            record.last_polled_at.isoformat() if record.last_polled_at else None,
        )

    @staticmethod
    def _deserialize(row: sqlite3.Row) -> JobRecord:
        return JobRecord(
            id=row["id"],
            generation_id=row["generation_id"],
            status=JobStatus(row["status"]),
            progress=row["progress"],
            provider=row["provider"],
            preset=row["preset"],
            views=tuple(json.loads(row["views_json"])),
            provider_task_id=row["provider_task_id"],
            artifact_path=row["artifact_path"],
            thumbnail_path=row["thumbnail_path"],
            mesh_metadata=json.loads(row["mesh_metadata_json"])
            if row["mesh_metadata_json"]
            else None,
            warnings=tuple(json.loads(row["warnings_json"])),
            error_code=row["error_code"],
            error_message=row["error_message"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            last_polled_at=datetime.fromisoformat(row["last_polled_at"])
            if row["last_polled_at"]
            else None,
        )
