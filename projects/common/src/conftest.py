import os
from collections.abc import Generator
from typing import Any
from unittest.mock import Mock
import pytest
from fastapi.testclient import TestClient

from hexrepo_db.interface import UOW
from app.adaptor.db.sql.uow import SqlUOW
from hexrepo_db import UOW


# Create local file db
SQLITE_DATABASE_URL = "sqlite:///test.db"
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost:5432/test_db"


def reset_db(uow: UOW, drop_only: bool = False):
    try:
        uow.drop_all()
    except:
        pass
    if not drop_only:
        uow.create_all()


@pytest.fixture
def uow_lite() -> Generator[UOW, None, None]:
    """
    Return db adaptor with initialised DB & DB session.
    """
    uow = SqlUOW(db_url=SQLITE_DATABASE_URL)
    # Create DB session
    with uow.transaction() as session:
        reset_db(uow)
        yield uow


@pytest.fixture
def uow() -> Generator[UOW, None, None]:
    """
    Return db adaptor with initialised DB & DB session.
    """
    uow = SqlUOW(db_url=SQLALCHEMY_DATABASE_URL)
    # Create DB session
    with uow.transaction() as session:
        reset_db(uow)
        yield uow


@pytest.fixture(scope="function")
def create_tables(uow: UOW):
    reset_db(uow)


@pytest.fixture(scope="function")
def drop_tables(uow: UOW):
    reset_db(uow, drop_only=True)


@pytest.fixture
def client(uow):
    from app.interactor.api.fastapi import app
    from app.interactor.dependencies import get_uow

    def get_uow_override():
        yield uow

    app.dependency_overrides[get_uow] = get_uow_override
    return TestClient(app)


@pytest.fixture
def example_data():
    return {
        "name": "test",
        "url": "https://test.com",
        "location": "test location",
    }
