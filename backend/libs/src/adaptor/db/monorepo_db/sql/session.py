import contextlib
from typing import Dict, Iterator, Optional

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Connection, Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import event

from monorepo_db.config import config


class DatabaseSessionManager:
    def __init__(self, host: str, engine_args: Optional[Dict] = None):
        self._engine_args = engine_args or dict(
            poolclass=sqlalchemy.pool.NullPool,
            future=True,
            echo=config.DB_SQL_LOGGING,
        )
        if config.DB_SSL_CONNECTION:
            self._engine_args["connect_args"] = {"sslmode": "require"}

        self._engine: Engine = create_engine(host, **self._engine_args)
        self._sessionmaker = sessionmaker(autocommit=False, bind=self._engine)
        self._query_counts = {}
        self._session: Optional[Session] = None

    def close(self):
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
    def transaction(self) -> Iterator[Session]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")
        
        if self._session:
            return self._session

        self._session = self._sessionmaker()
        with self.count_queries(self._session.connection()):
            try:
                yield self._session
                self._session.commit()
            except Exception:
                self._session.rollback()
                raise
            finally:
                self._session.close()
                self.close()
        self._session = None

    @contextlib.contextmanager
    def count_queries(self, conn):
        # Wrap sessions and track number of queries executed
        def before_cursor_execute(
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
    def session_query_count(self, session=None):
        # Return number of queries from first session for testing
        if session is not None:
            return self._query_counts[session.connection()]
        elif self._query_counts:
            return list(self._query_counts.values())[0]
        else:
            raise RuntimeError("No DB session initialized")
