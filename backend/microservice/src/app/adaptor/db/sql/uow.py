import contextlib
from typing import Dict, Optional

from ..interface import UOW
from .session import DatabaseSessionManager
from .models.example import ExampleRepository


class SqlUOW(UOW):
    def __init__(self, db_url: str, required_filters: Optional[Dict] = None):
        self._db_url: str = db_url
        self._required_filters: Optional[Dict] = required_filters
        self._session = None
        self._session_manager: DatabaseSessionManager = DatabaseSessionManager(self._db_url)

    # Add transaction context manager
    @contextlib.contextmanager
    def transaction(self):
        with self._session_manager.session() as session:
            self._session = session
            yield session

    @property
    def session(self):
        if not self._sesion_manager and not self._session:
            raise RuntimeError("Session not initialised")
        return self._session

    @property
    def example(self) -> ExampleRepository:
        return ExampleRepository(
            session=self.session, required_filters=self._required_filters
        )

    # Used for testing
    def create_all(self):
        from .models.base_model import Base

        Base.metadata.create_all(self._session.get_bind())

    def drop_all(self):
        from .models.base_model import Base

        Base.metadata.drop_all(self._session.get_bind())
