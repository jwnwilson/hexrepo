import contextlib
from typing import Dict, Generator, Optional

from ..interface import UOW
from .session import DatabaseSessionManager
from .models.example import ExampleRepository


class SqlUOW(UOW):
    def __init__(self, db_url: str, required_filters: Optional[Dict] = None):
        self._db_url: str = db_url
        self._required_filters: Optional[Dict] = required_filters
        self.session_manager: DatabaseSessionManager = DatabaseSessionManager(self._db_url)

    # Add transaction context manager
    @contextlib.contextmanager
    def transaction(self) -> Generator[DatabaseSessionManager, None, None]:
        with self.session_manager.session():
            yield self.session_manager

    @property
    def session(self):
        return self.session_manager.session

    @property
    def example(self) -> ExampleRepository:
        return ExampleRepository(
            session=self.session_manager.session, required_filters=self._required_filters
        )

    # Used for testing
    def create_all(self):
        from .models.base_model import Base

        Base.metadata.create_all(self._session.get_bind())

    def drop_all(self):
        from .models.base_model import Base

        Base.metadata.drop_all(self._session.get_bind())
