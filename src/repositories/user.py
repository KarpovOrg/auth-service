from sqlalchemy import (
    select,
    update,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from models import User

from schemas import UserCreate

from .base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model=User)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(self.model).where(self.model.email == email)
        )
        return result.scalar_one_or_none()

    async def upsert_user(self, schema: UserCreate) -> User:
        stmt = (
            insert(self.model)
            .values(
                email=schema.email,
                name=schema.name,
                surname=schema.surname,
                password_hash=schema.password_hash,
                is_verified=schema.is_verified,
            )
            .on_conflict_do_nothing(index_elements=["email"])
            .returning(User)
        )

        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            return user

        return await self.get_by_email(email=str(schema.email))

    async def set_verified(self, user_id: int) -> User | None:
        stmt = (
            update(self.model)
            .where(self.model.id == user_id)
            .values(is_verified=True)
            .returning(User)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

