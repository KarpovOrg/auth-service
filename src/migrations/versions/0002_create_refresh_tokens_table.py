"""create refresh_tokens table

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-17 00:00:01.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op


revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "auth_schema"

def upgrade() -> None:
    op.execute(sa.schema.CreateSchema(SCHEMA, if_not_exists=True))

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users_schema.users.id"],
            name=op.f("fk_refresh_tokens_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["auth_schema.sessions.id"],
            name=op.f("fk_refresh_tokens_session_id_sessions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_refresh_tokens")),
        schema="auth_schema",
    )
    op.create_index(op.f("ix_auth_schema_refresh_tokens_id"), "refresh_tokens", ["id"], unique=False, schema="auth_schema")
    op.create_index(op.f("ix_auth_schema_refresh_tokens_user_id"), "refresh_tokens", ["user_id"], unique=False, schema="auth_schema")
    op.create_index(op.f("ix_auth_schema_refresh_tokens_session_id"), "refresh_tokens", ["session_id"], unique=False, schema="auth_schema")


def downgrade() -> None:
    op.drop_index(op.f("ix_auth_schema_refresh_tokens_session_id"), table_name="refresh_tokens", schema="auth_schema")
    op.drop_index(op.f("ix_auth_schema_refresh_tokens_user_id"), table_name="refresh_tokens", schema="auth_schema")
    op.drop_index(op.f("ix_auth_schema_refresh_tokens_id"), table_name="refresh_tokens", schema="auth_schema")
    op.drop_table("refresh_tokens", schema="auth_schema")
