"""Create body, asset, try-on job and step metadata tables.

Revision ID: 20261018_0001
Revises:
"""

from alembic import op
import sqlalchemy as sa

revision = "20261018_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bodies",
        sa.Column("body_id", sa.String(100), primary_key=True),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("method", sa.String(100), nullable=False),
        sa.Column("schema_json", sa.JSON()),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("error_code", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("kind IN ('mock_analyzed', 'mpfb')", name="ck_bodies_kind"),
        sa.CheckConstraint("status IN ('processing', 'ready', 'failed')", name="ck_bodies_status"),
    )
    op.create_index("ix_bodies_kind_status", "bodies", ["kind", "status"])
    op.create_table(
        "tryon_jobs",
        sa.Column("job_id", sa.String(100), primary_key=True),
        sa.Column("body_id", sa.String(100), sa.ForeignKey("bodies.body_id"), nullable=False),
        sa.Column("garment_id", sa.String(100), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("method", sa.String(100), nullable=False),
        sa.Column("notes_json", sa.JSON(), nullable=False),
        sa.Column("request_json", sa.JSON(), nullable=False),
        sa.Column("result_json", sa.JSON()),
        sa.Column("error_json", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status IN ('pending', 'running', 'completed', 'failed')", name="ck_tryon_jobs_status"),
        sa.CheckConstraint("duration_ms IS NULL OR duration_ms >= 0", name="ck_tryon_jobs_duration"),
    )
    op.create_index("ix_tryon_jobs_body_status", "tryon_jobs", ["body_id", "status"])
    op.create_index("ix_tryon_jobs_created_at", "tryon_jobs", ["created_at"])
    op.create_table(
        "assets",
        sa.Column("asset_id", sa.String(100), primary_key=True),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("storage_scope", sa.String(16), nullable=False),
        sa.Column("storage_key", sa.String(255), nullable=False),
        sa.Column("public_name", sa.String(128), unique=True),
        sa.Column("media_type", sa.String(100), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("body_id", sa.String(100), sa.ForeignKey("bodies.body_id")),
        sa.Column("job_id", sa.String(100), sa.ForeignKey("tryon_jobs.job_id")),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("kind IN ('original_image', 'foreground_image', 'mesh', 'texture', 'glb')", name="ck_assets_kind"),
        sa.CheckConstraint("status IN ('available', 'missing', 'failed')", name="ck_assets_status"),
        sa.CheckConstraint("storage_scope IN ('fixture', 'managed')", name="ck_assets_scope"),
        sa.CheckConstraint("byte_size >= 0", name="ck_assets_byte_size"),
    )
    op.create_index("ix_assets_body_kind", "assets", ["body_id", "kind"])
    op.create_index("ix_assets_job_kind", "assets", ["job_id", "kind"])
    op.create_table(
        "job_steps",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.String(100), sa.ForeignKey("tryon_jobs.job_id", ondelete="CASCADE"), nullable=False),
        sa.Column("step", sa.String(100), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("error_code", sa.String(100)),
        sa.Column("message", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.CheckConstraint("status IN ('pending', 'running', 'completed', 'failed')", name="ck_job_steps_status"),
        sa.CheckConstraint("duration_ms IS NULL OR duration_ms >= 0", name="ck_job_steps_duration"),
    )
    op.create_index("ix_job_steps_job_started", "job_steps", ["job_id", "started_at"])


def downgrade() -> None:
    op.drop_index("ix_job_steps_job_started", table_name="job_steps")
    op.drop_table("job_steps")
    op.drop_index("ix_assets_job_kind", table_name="assets")
    op.drop_index("ix_assets_body_kind", table_name="assets")
    op.drop_table("assets")
    op.drop_index("ix_tryon_jobs_created_at", table_name="tryon_jobs")
    op.drop_index("ix_tryon_jobs_body_status", table_name="tryon_jobs")
    op.drop_table("tryon_jobs")
    op.drop_index("ix_bodies_kind_status", table_name="bodies")
    op.drop_table("bodies")
