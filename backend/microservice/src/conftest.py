import os
from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient

from src.app.adaptor.db.interface import UOW
from src.app.adaptor.db.sql.uow import SqlUOW

# Silence SQLALchemy deprecation warning until we can upgrade
os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"

# Create local file db
SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"

@pytest.fixture
def uow() -> Generator[UOW, None, None]:
    """
    Return db adaptor with initialised DB & DB session.
    """
    uow = SqlUOW(db_url=SQLALCHEMY_DATABASE_URL)
    # Create tables
    uow.init_db()
    # Create DB session
    with uow.transaction() as session:
        yield uow


@pytest.fixture
def client(uow):
    from app.interactor.api.fastapi import app
    from app.interactor.api.fastapi.dependencies import get_uow

    def get_uow_override():
        yield uow

    app.dependency_overrides[get_uow] = get_uow_override
    return TestClient(app)
