"""SQLAlchemy metadata. Binary assets live on disk; rows store safe references."""

from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class BodyRecord(Base):
    __tablename__ = "bodies"
    body_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    method: Mapped[str] = mapped_column(String(100), nullable=False)
    schema_json: Mapped[dict | None] = mapped_column(JSON)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    error_code: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    __table_args__ = (
        CheckConstraint("kind IN ('mock_analyzed', 'mpfb')", name="ck_bodies_kind"),
        CheckConstraint("status IN ('processing', 'ready', 'failed')", name="ck_bodies_status"),
        Index("ix_bodies_kind_status", "kind", "status"),
    )


class JobRecord(Base):
    __tablename__ = "tryon_jobs"
    job_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    body_id: Mapped[str] = mapped_column(ForeignKey("bodies.body_id"), nullable=False)
    garment_id: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    method: Mapped[str] = mapped_column(String(100), nullable=False)
    notes_json: Mapped[list] = mapped_column(JSON, nullable=False)
    request_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    result_json: Mapped[dict | None] = mapped_column(JSON)
    error_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'running', 'completed', 'failed')", name="ck_tryon_jobs_status"),
        CheckConstraint("duration_ms IS NULL OR duration_ms >= 0", name="ck_tryon_jobs_duration"),
        Index("ix_tryon_jobs_body_status", "body_id", "status"),
        Index("ix_tryon_jobs_created_at", "created_at"),
    )


class AssetRecord(Base):
    __tablename__ = "assets"
    asset_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    storage_scope: Mapped[str] = mapped_column(String(16), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False)
    public_name: Mapped[str | None] = mapped_column(String(128), unique=True)
    media_type: Mapped[str] = mapped_column(String(100), nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    body_id: Mapped[str | None] = mapped_column(ForeignKey("bodies.body_id"))
    job_id: Mapped[str | None] = mapped_column(ForeignKey("tryon_jobs.job_id"))
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    __table_args__ = (
        CheckConstraint("kind IN ('original_image', 'foreground_image', 'mesh', 'texture', 'glb')", name="ck_assets_kind"),
        CheckConstraint("status IN ('available', 'missing', 'failed')", name="ck_assets_status"),
        CheckConstraint("storage_scope IN ('fixture', 'managed')", name="ck_assets_scope"),
        CheckConstraint("byte_size >= 0", name="ck_assets_byte_size"),
        Index("ix_assets_body_kind", "body_id", "kind"),
        Index("ix_assets_job_kind", "job_id", "kind"),
    )


class JobStepRecord(Base):
    __tablename__ = "job_steps"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("tryon_jobs.job_id", ondelete="CASCADE"), nullable=False)
    step: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(100))
    message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'running', 'completed', 'failed')", name="ck_job_steps_status"),
        CheckConstraint("duration_ms IS NULL OR duration_ms >= 0", name="ck_job_steps_duration"),
        Index("ix_job_steps_job_started", "job_id", "started_at"),
    )
