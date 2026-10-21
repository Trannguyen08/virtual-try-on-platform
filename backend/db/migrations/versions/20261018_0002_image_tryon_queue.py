"""Add durable image try-on queue.

Revision ID: 20261018_0002
Revises: 20261018_0001
"""

from alembic import op
import sqlalchemy as sa

revision = "20261018_0002"
down_revision = "20261018_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "image_tryon_jobs",
        sa.Column("job_id", sa.String(100), primary_key=True),
        sa.Column("body_id", sa.String(100), sa.ForeignKey("bodies.body_id"), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("request_json", sa.JSON(), nullable=False),
        sa.Column("result_json", sa.JSON()),
        sa.Column("error_json", sa.JSON()),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("leased_until", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed')",
            name="ck_image_tryon_jobs_status",
        ),
        sa.CheckConstraint("attempt_count >= 0", name="ck_image_tryon_jobs_attempts"),
    )
    op.create_index(
        "ix_image_tryon_jobs_status_created",
        "image_tryon_jobs", ["status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_image_tryon_jobs_status_created", table_name="image_tryon_jobs")
    op.drop_table("image_tryon_jobs")
