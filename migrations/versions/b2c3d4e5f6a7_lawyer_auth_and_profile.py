"""lawyer auth accounts and multi-value profile fields

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-19 02:40:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_users_email"), ["email"], unique=True)
        batch_op.create_index(batch_op.f("ix_users_role"), ["role"], unique=False)

    with op.batch_alter_table("lawyers", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("bar_council_number", sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column("address", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("mobile", sa.String(length=20), nullable=True))
        batch_op.add_column(
            sa.Column(
                "approval_status",
                sa.String(length=20),
                nullable=False,
                server_default="pending",
            )
        )
        batch_op.add_column(sa.Column("rejection_reason", sa.Text(), nullable=True))
        batch_op.create_index(batch_op.f("ix_lawyers_user_id"), ["user_id"], unique=True)
        batch_op.create_index(
            batch_op.f("ix_lawyers_bar_council_number"),
            ["bar_council_number"],
            unique=True,
        )
        batch_op.create_index(
            batch_op.f("ix_lawyers_approval_status"),
            ["approval_status"],
            unique=False,
        )
        batch_op.create_foreign_key(
            "fk_lawyers_user_id_users",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )

    op.create_table(
        "lawyer_practice_areas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lawyer_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["lawyer_id"], ["lawyers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lawyer_id", "name", name="uq_lawyer_practice_area"),
    )
    with op.batch_alter_table("lawyer_practice_areas", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_lawyer_practice_areas_lawyer_id"),
            ["lawyer_id"],
            unique=False,
        )

    op.create_table(
        "lawyer_languages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lawyer_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["lawyer_id"], ["lawyers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lawyer_id", "name", name="uq_lawyer_language"),
    )
    with op.batch_alter_table("lawyer_languages", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_lawyer_languages_lawyer_id"),
            ["lawyer_id"],
            unique=False,
        )

    op.create_table(
        "lawyer_locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lawyer_id", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(length=80), nullable=False),
        sa.Column("city", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["lawyer_id"], ["lawyers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lawyer_id", "state", "city", name="uq_lawyer_location"),
    )
    with op.batch_alter_table("lawyer_locations", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_lawyer_locations_lawyer_id"),
            ["lawyer_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_lawyer_locations_city"),
            ["city"],
            unique=False,
        )

    conn = op.get_bind()
    rows = conn.execute(
        sa.text(
            "SELECT id, practice_area, city, state, is_approved FROM lawyers"
        )
    ).fetchall()
    for row in rows:
        lawyer_id, practice_area, city, state, is_approved = row
        if practice_area:
            conn.execute(
                sa.text(
                    "INSERT INTO lawyer_practice_areas (lawyer_id, name) "
                    "VALUES (:lawyer_id, :name)"
                ),
                {"lawyer_id": lawyer_id, "name": practice_area},
            )
        if city:
            conn.execute(
                sa.text(
                    "INSERT INTO lawyer_locations (lawyer_id, state, city) "
                    "VALUES (:lawyer_id, :state, :city)"
                ),
                {
                    "lawyer_id": lawyer_id,
                    "state": state or "",
                    "city": city,
                },
            )
        status = "approved" if is_approved else "pending"
        conn.execute(
            sa.text(
                "UPDATE lawyers SET approval_status = :status WHERE id = :id"
            ),
            {"status": status, "id": lawyer_id},
        )

    with op.batch_alter_table("lawyers", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_lawyers_city"))
        batch_op.drop_index(batch_op.f("ix_lawyers_practice_area"))
        batch_op.drop_column("practice_area")
        batch_op.drop_column("city")
        batch_op.drop_column("state")
        batch_op.drop_column("email")


def downgrade():
    with op.batch_alter_table("lawyers", schema=None) as batch_op:
        batch_op.add_column(sa.Column("email", sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column("state", sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column("city", sa.String(length=80), nullable=False, server_default=""))
        batch_op.add_column(
            sa.Column("practice_area", sa.String(length=80), nullable=False, server_default="")
        )
        batch_op.create_index(batch_op.f("ix_lawyers_city"), ["city"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_lawyers_practice_area"), ["practice_area"], unique=False
        )

    conn = op.get_bind()
    lawyers = conn.execute(sa.text("SELECT id FROM lawyers")).fetchall()
    for (lawyer_id,) in lawyers:
        area = conn.execute(
            sa.text(
                "SELECT name FROM lawyer_practice_areas WHERE lawyer_id = :id LIMIT 1"
            ),
            {"id": lawyer_id},
        ).fetchone()
        loc = conn.execute(
            sa.text(
                "SELECT city, state FROM lawyer_locations WHERE lawyer_id = :id LIMIT 1"
            ),
            {"id": lawyer_id},
        ).fetchone()
        conn.execute(
            sa.text(
                "UPDATE lawyers SET practice_area = :area, city = :city, state = :state "
                "WHERE id = :id"
            ),
            {
                "area": area[0] if area else "Civil",
                "city": loc[0] if loc else "Delhi",
                "state": loc[1] if loc else None,
                "id": lawyer_id,
            },
        )

    with op.batch_alter_table("lawyer_locations", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_lawyer_locations_city"))
        batch_op.drop_index(batch_op.f("ix_lawyer_locations_lawyer_id"))
    op.drop_table("lawyer_locations")

    with op.batch_alter_table("lawyer_languages", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_lawyer_languages_lawyer_id"))
    op.drop_table("lawyer_languages")

    with op.batch_alter_table("lawyer_practice_areas", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_lawyer_practice_areas_lawyer_id"))
    op.drop_table("lawyer_practice_areas")

    with op.batch_alter_table("lawyers", schema=None) as batch_op:
        batch_op.drop_constraint("fk_lawyers_user_id_users", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_lawyers_approval_status"))
        batch_op.drop_index(batch_op.f("ix_lawyers_bar_council_number"))
        batch_op.drop_index(batch_op.f("ix_lawyers_user_id"))
        batch_op.drop_column("rejection_reason")
        batch_op.drop_column("approval_status")
        batch_op.drop_column("mobile")
        batch_op.drop_column("address")
        batch_op.drop_column("bar_council_number")
        batch_op.drop_column("user_id")

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_users_role"))
        batch_op.drop_index(batch_op.f("ix_users_email"))
    op.drop_table("users")
