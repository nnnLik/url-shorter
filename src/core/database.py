from collections.abc import AsyncGenerator
from dataclasses import dataclass, field

from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.asyncio.session import AsyncSession

from config import settings


@dataclass
class DatabaseSession:
    _engine: AsyncEngine = field(init=False)
    _session_factory: async_sessionmaker[AsyncSession] = field(init=False)

    def __post_init__(self) -> None:
        db_url = str(settings.database.URL).replace('postgresql://', 'postgresql+asyncpg://', 1)
        self._engine: AsyncEngine = create_async_engine(
            url=db_url,
            echo=settings.database.ECHO,
            echo_pool=settings.database.ECHO_POOL,
            pool_size=settings.database.POOL_SIZE,
            max_overflow=settings.database.MAX_OVERFLOW,
        )
        self._session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker[AsyncSession](
            bind=self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        await self._engine.dispose()
        logger.info('Database engine disposed')

    async def session_getter(self) -> AsyncGenerator[AsyncSession]:
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


db_session: DatabaseSession = DatabaseSession()
