from typing import Dict, Generator

import pytest

from monorepo_db import UOW
from monorepo_db.sql import get_sql_db_url
from monorepo_db.sql.models.example import ExampleCreateDTO, ExampleDTO, SqlUOW


@pytest.fixture
def uow() -> Generator[UOW, None, None]:
    db_url = get_sql_db_url()
    uow = SqlUOW(db_url=db_url)
    with uow.transaction():
        yield uow


@pytest.fixture(scope="function", autouse=True)
def create_tables(uow: UOW) -> None:
    uow.drop_all()
    uow.create_all()


@pytest.fixture
def example_records(uow: UOW) -> Dict[str, ExampleDTO]:
    example_1: ExampleDTO = uow.example.create(
        ExampleCreateDTO(name="example1", url="example1.com")
    )
    example_2: ExampleDTO = uow.example.create(
        ExampleCreateDTO(name="example2", url="example2.com")
    )
    return {"example_1": example_1, "example_2": example_2}
