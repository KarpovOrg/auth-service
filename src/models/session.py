from sqlalchemy import (
    Boolean,
    Integer,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from constants import DeviceType

from .base import Base

from .mixins import (
    IdMixin,
    UidMixin,
    CreatedAtMixin,
)


class Session(Base, IdMixin, UidMixin, CreatedAtMixin):
    __tablename__ = "sessions"
    __table_args__ = {
        "schema": "auth_schema",
    }

    device_type: Mapped[str] = mapped_column(
        ENUM(
            DeviceType,
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        )
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users_schema.users.id", ondelete="CASCADE"),
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )