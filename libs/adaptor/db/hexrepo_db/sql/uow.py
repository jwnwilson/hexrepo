import contextlib
from typing import Dict, Generator, Optional

from sqlalchemy.orm import Session

from ..interface import UOW
from .session import DatabaseSessionManager


class BaseSqlUOW(UOW):
    session_manager_map: Dict[str, DatabaseSessionManager] = {}
    
    def __init__(self, db_url: str, required_filters: Optional[Dict[str, str]] = None):
        self._db_url: str = db_url
        self._required_filters: Optional[Dict[str, str]] = required_filters
        if db_url not in self.session_manager_map:
            self.session_manager_map[db_url] = DatabaseSessionManager(db_url)
        self.session_manager: DatabaseSessionManager = self.session_manager_map[db_url]

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
