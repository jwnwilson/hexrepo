import contextlib
from typing import Any, Dict, Generator, Iterator, Optional

import sqlalchemy
from sqlalchemy import create_engine, event
from sqlalchemy.engine.base import Connection, Engine
from sqlalchemy.orm import Session, sessionmaker

from hexrepo_db.config import config


class DatabaseSessionManager:
    _engine_map: Dict[str, Engine] = {}

    def __init__(self, host: str, engine_args: Optional[Dict[str, Any]] = None):
        self._engine_args = engine_args or dict(
            future=True,
            echo=config.DB_SQL_LOGGING,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_recycle=10,
            pool_timeout=5,

        )
        if config.DB_SSL_CONNECTION:
            self._engine_args["connect_args"] = {"sslmode": "require"}
        # Sets application name for debugging in pg_stat_activity table if using postgres
        host += "?application_name=sqlalchemy"

        if host not in self._engine_map:
            self._engine_map[host] = create_engine(host, **self._engine_args)
        self._engine: Optional[Engine] = self._engine_map[host]
        self._sessionmaker: Optional[sessionmaker[Session]] = sessionmaker(
            autocommit=False, bind=self._engine
        )
        self._query_counts: Dict[Connection, int] = {}
        self._session: Optional[Session] = None

    def close(self) -> None:
        if self._engine is None:
            raise RuntimeError("DatabaseSessionManager is not initialized")
        self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @property
    def session(self) -> Session:
        if self._session is None:
            raise RuntimeError("DatabaseSessionManager is not initialized")
        return self._session

    @contextlib.contextmanager
    def connect(self) -> Iterator[Connection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                connection.rollback()
                raise

    @contextlib.contextmanager
    def transaction(self) -> Generator[Session, None, None]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        if self._session:
            raise RuntimeError("Session already initialized, transaction in progress")

        self._session = self._sessionmaker()
        assert self._session is not None, "Session not initialized"
        with self.count_queries(self._session.connection()):
            try:
                yield self._session
                self._session.commit()
            except Exception:
                self._session.rollback()
                raise
            finally:
                self._session.close()

        self._session = None

    @contextlib.contextmanager
    def count_queries(self, conn: Connection) -> Generator[int, None, None]:
        # Wrap sessions and track number of queries executed
        def before_cursor_execute(  # type: ignore
            conn, cursor, statement, parameters, context, executemany
        ):
            self._query_counts[conn] += 1

        self._query_counts[conn] = 0
        event.listen(conn, "before_cursor_execute", before_cursor_execute)
        try:
            yield self._query_counts[conn]
        finally:
            event.remove(conn, "before_cursor_execute", before_cursor_execute)

    @property
    def session_query_count(self, session: Optional[Session] = None) -> int:
        # Return number of queries from first session for testing
        if session is not None:
            return self._query_counts[session.connection()]
        elif self._query_counts:
            return list(self._query_counts.values())[0]
        else:
            raise RuntimeError("No DB session initialized")
