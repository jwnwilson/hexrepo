from typing import Dict, Generator

import pytest

from monorepo_db import UOW
from monorepo_db.nosql import MongoUOW, MongoRepository, DynamoUOW, DynamoRepository
from monorepo_db.sql.models.example import ExampleCreateDTO, ExampleDTO


@pytest.fixture
def uow_dynamo() -> Generator[UOW, None, None]:
    db_url = "http://localhost:8000"
    uow = DynamoUOW(db_url=db_url)
    # with uow.transaction():
    yield uow


@pytest.fixture
def uow_mongo() -> Generator[UOW, None, None]:
    db_url = "http://localhost:27017"
    uow = MongoUOW(db_url=db_url)
    # with uow.transaction():
    yield uow


@pytest.fixture(scope="function")
def create_tables_dynamo(uow_dynamo: UOW) -> None:
    uow_dynamo.drop_all()
    uow_dynamo.create_all()


@pytest.fixture(scope="function")
def create_tables_mongo(uow_mongo: UOW) -> None:
    uow_mongo.drop_all()
    uow_mongo.create_all()
