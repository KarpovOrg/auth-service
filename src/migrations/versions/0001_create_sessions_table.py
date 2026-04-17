"""create sessions table

Revision ID: 0001
Revises:
Create Date: 2026-04-17 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "auth_schema"

def upgrade() -> None:
    op.execute(sa.schema.CreateSchema(SCHEMA, if_not_exists=True))

    op.execute(
        "CREATE TYPE auth_schema.devicetype AS ENUM ('desktop', 'mobile', 'tablet', 'unknown')"
    )

    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uid", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column(
            "device_type",
            postgresql.ENUM(
                "desktop",
                "mobile",
                "tablet",
                "unknown",
                name="devicetype",
                schema="auth_schema",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users_schema.users.id"],
            name=op.f("fk_sessions_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessions")),
        schema="auth_schema",
    )
    op.create_index(op.f("ix_auth_schema_sessions_id"), "sessions", ["id"], unique=False, schema="auth_schema")
    op.create_index(op.f("ix_auth_schema_sessions_uid"), "sessions", ["uid"], unique=True, schema="auth_schema")
    op.create_index(op.f("ix_auth_schema_sessions_user_id"), "sessions", ["user_id"], unique=False, schema="auth_schema")


def downgrade() -> None:
    op.drop_index(op.f("ix_auth_schema_sessions_user_id"), table_name="sessions", schema="auth_schema")
    op.drop_index(op.f("ix_auth_schema_sessions_uid"), table_name="sessions", schema="auth_schema")
    op.drop_index(op.f("ix_auth_schema_sessions_id"), table_name="sessions", schema="auth_schema")
    op.drop_table("sessions", schema="auth_schema")

    op.execute("DROP TYPE IF EXISTS auth_schema.devicetype")

    op.execute("DROP SCHEMA IF EXISTS auth_schema CASCADE")

