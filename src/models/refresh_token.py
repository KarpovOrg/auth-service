from datetime import datetime

from sqlalchemy import (
    String,
    Boolean,
    Integer,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from .base import Base

from .mixins import (
    IdMixin,
    CreatedAtMixin,
)


class RefreshToken(Base, IdMixin, CreatedAtMixin):
    __tablename__ = "refresh_tokens"
    __table_args__ = {
        "schema": "auth_schema",
    }

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users_schema.users.id", ondelete="CASCADE"),
        index=True,
    )
    session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("auth_schema.sessions.id", ondelete="CASCADE"),
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

