from typing import Generator

import pytest

from monorepo_db import UOW
from monorepo_db.nosql import DynamoUOW, MongoUOW


@pytest.fixture
def uow_dynamo() -> Generator[UOW, None, None]:
    db_url = "http://localhost:8000"
    uow = DynamoUOW(db_url=db_url)
    # with uow.transaction():
    yield uow


@pytest.fixture
def uow_mongo() -> Generator[UOW, None, None]:
    db_url = "mongodb://localhost:27017/test_db"
    uow = MongoUOW(db_url=db_url)
    # with uow.transaction():
    yield uow


@pytest.fixture(scope="function", autouse=True)
def create_tables_dynamo(uow_dynamo: UOW) -> None:
    uow_dynamo.drop_all()
    uow_dynamo.create_all()


@pytest.fixture(scope="function", autouse=True)
def create_tables_mongo(uow_mongo: UOW) -> None:
    uow_mongo.drop_all()
    uow_mongo.create_all()
