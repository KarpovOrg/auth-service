from datetime import (
    datetime,
    timezone,
)

from sqlalchemy import (
    select,
    and_,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession

from models import RefreshToken

from .base import BaseRepository


class RefreshTokenRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model=RefreshToken)

    async def get_valid_by_hash(self, token_hash: str) -> RefreshToken | None:
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            select(self.model).where(
                and_(
                    self.model.token_hash == token_hash,
                    self.model.revoked == False,
                    self.model.expires_at > now,
                )
            )
        )
        return result.scalar_one_or_none()

    async def revoke(self, token_id: int) -> None:
        await self.session.execute(
            update(self.model)
            .where(self.model.id == token_id)
            .values(revoked=True)
        )