from typing import Dict, Generator

import pytest

from monorepo_db import UOW
from monorepo_db.nosql import DynamoUOW, MongoUOW
from monorepo_db.sql.models.example import ExampleCreateDTO, ExampleDTO


@pytest.fixture
def uow_dynamo() -> Generator[UOW, None, None]:
    db_url = "http://0.0.0.0:8000"
    uow = DynamoUOW(db_url=db_url)
    # with uow.transaction():
    yield uow


@pytest.fixture
def uow_mongo() -> Generator[UOW, None, None]:
    db_url = "mongodb://0.0.0.0:27017/test_db"
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


@pytest.fixture
def example_records_dynamo(uow_dynamo: UOW) -> Dict[str, ExampleDTO]:
    example_1: ExampleDTO = uow_dynamo.example.create(
        ExampleCreateDTO(name="example1", url="example1.com")
    )
    example_2: ExampleDTO = uow_dynamo.example.create(
        ExampleCreateDTO(name="example2", url="example2.com")
    )

    return {"example_1": example_1, "example_2": example_2}


@pytest.fixture
def example_records_mongo(uow_mongo: UOW) -> Dict[str, ExampleDTO]:
    example_1: ExampleDTO = uow_mongo.example.create(
        ExampleCreateDTO(name="example1", url="example1.com")
    )
    example_2: ExampleDTO = uow_mongo.example.create(
        ExampleCreateDTO(name="example2", url="example2.com")
    )
    return {"example_1": example_1, "example_2": example_2}
