import os
from collections.abc import Generator

# Silence SQLALchemy deprecation warning until we can upgrade
os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"

import pytest
from fastapi.testclient import TestClient

from app.adapter.db import SQLALchemyAdapter
from app.ports.db import DbAdapter

# Create local file db
SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"


@pytest.fixture
def db_adapter() -> DbAdapter:
    """
    Return db adapter without DB session
    """
    return SQLALchemyAdapter(
        SQLALCHEMY_DATABASE_URL,
        engine_args={"connect_args": {"check_same_thread": False}},
    )


@pytest.fixture
def db(db_adapter: DbAdapter) -> Generator[DbAdapter, None, None]:
    """
    Return db adapter with initialised DB & DB session.
    """
    # Create tables
    db_adapter.init_db()
    # Create DB session
    with db_adapter.transaction() as session:
        yield db_adapter


@pytest.fixture
def client(db):
    from app.adapter.fastapi import app
    from app.adapter.fastapi.dependencies import get_db

    def get_db_override():
        yield db

    app.dependency_overrides[get_db] = get_db_override
    return TestClient(app)
