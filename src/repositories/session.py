from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from models import Session

from .base import BaseRepository


class SessionRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model=Session)

    async def deactivate(self, session_id: int) -> None:   # НОВОЕ
        await self.session.execute(
            update(self.model)
            .where(self.model.id == session_id)
            .values(is_active=False)
        )