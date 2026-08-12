"""add lawyers table

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-08-12 21:40:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "a1b2c3d4e5f6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "lawyers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=140), nullable=False),
        sa.Column("practice_area", sa.String(length=80), nullable=False),
        sa.Column("city", sa.String(length=80), nullable=False),
        sa.Column("state", sa.String(length=80), nullable=True),
        sa.Column("years_experience", sa.Integer(), nullable=False),
        sa.Column("photo_url", sa.String(length=500), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("is_approved", sa.Boolean(), nullable=False),
        sa.Column("is_featured", sa.Boolean(), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("lawyers", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_lawyers_city"), ["city"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_lawyers_is_approved"), ["is_approved"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_lawyers_is_featured"), ["is_featured"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_lawyers_practice_area"), ["practice_area"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_lawyers_slug"), ["slug"], unique=True)


def downgrade():
    with op.batch_alter_table("lawyers", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_lawyers_slug"))
        batch_op.drop_index(batch_op.f("ix_lawyers_practice_area"))
        batch_op.drop_index(batch_op.f("ix_lawyers_is_featured"))
        batch_op.drop_index(batch_op.f("ix_lawyers_is_approved"))
        batch_op.drop_index(batch_op.f("ix_lawyers_city"))

    op.drop_table("lawyers")
