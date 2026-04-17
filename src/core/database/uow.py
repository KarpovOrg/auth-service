from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
)

from repositories import (
    UserRepository,
    SessionRepository,
    RefreshTokenRepository,
)


class UnitOfWork:
    def __init__(
            self,
            session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._session_factory = session_factory
        self.session = None

    async def __aenter__(self) -> "UnitOfWork":
        self.session = await self._session_factory().__aenter__()

        self.user_repository = UserRepository(session=self.session)
        self.session_repository = SessionRepository(session=self.session)
        self.refresh_token_repository = RefreshTokenRepository(session=self.session)

        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type is not None:
                await self.session.rollback()
        finally:
            await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()