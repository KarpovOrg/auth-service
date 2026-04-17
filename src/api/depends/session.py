from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from core.database import db_client


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_client.get_session():
        yield session