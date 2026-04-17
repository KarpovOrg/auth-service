from collections.abc import AsyncGenerator

from typing import Any

from core.database import (
    UnitOfWork,
    db_client,
)


async def get_uow() -> AsyncGenerator[UnitOfWork, Any]:
    async with UnitOfWork(session_factory=db_client.session_factory) as uow:
        yield uow