import contextlib
from typing import AsyncGenerator, Dict, Generator, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ..interface import UOW
from .session import AsyncDatabaseSessionManager, DatabaseSessionManager


class BaseSqlUOW(UOW):
    def __init__(self, db_url: str, required_filters: Optional[Dict[str, str]] = None):
        self._db_url: str = db_url
        self._required_filters: Optional[Dict[str, str]] = required_filters
        self.session_manager: DatabaseSessionManager = DatabaseSessionManager(
            self._db_url
        )

    @contextlib.contextmanager
    def transaction(self) -> Generator[DatabaseSessionManager, None, None]:
        with self.session_manager.transaction():
            yield self.session_manager

    @property
    def session(self) -> "Session":
        return self.session_manager.session

    # Used for testing
    def create_all(self) -> None:
        from .models.base_model import Base

        Base.metadata.create_all(self.session.get_bind())

    def drop_all(self) -> None:
        from .models.base_model import Base

        Base.metadata.drop_all(self.session.get_bind())
        self.session.execute(text("DROP TABLE IF EXISTS alembic_version;"))
        self.session.commit()


class AsyncBaseSqlUOW(UOW):
    def __init__(self, db_url: str, required_filters: Optional[Dict[str, str]] = None):
        self._db_url: str = db_url
        self._required_filters: Optional[Dict[str, str]] = required_filters
        self.session_manager: AsyncDatabaseSessionManager = AsyncDatabaseSessionManager(
            self._db_url
        )

    @contextlib.asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncDatabaseSessionManager, None]:
        async with self.session_manager.transaction():
            yield self.session_manager

    @property
    def session(self) -> AsyncSession:
        return self.session_manager.session

    # Used for testing
    async def create_all(self) -> None:
        from .models.base_model import Base

        async with self.session_manager.connect() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self) -> None:
        from .models.base_model import Base

        async with self.session_manager.connect() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.execute(text("DROP TABLE IF EXISTS alembic_version;"))
            await conn.commit()
