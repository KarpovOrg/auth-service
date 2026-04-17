from typing import Annotated

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from .session import get_db

from repositories import UserRepository


def get_user_repository(
        session: Annotated[
            AsyncSession,
            Depends(get_db),
        ],
) -> UserRepository:
    return UserRepository(session=session)