from typing import Generator
import pytest

from monorepo_db import UOW
from monorepo_db.sql import get_sql_db_url
from monorepo_db.sql.models.example import SqlUOW


@pytest.fixture
def uow() -> Generator[UOW, None, None]:
    db_url = get_sql_db_url()
    uow = SqlUOW(db_url=db_url)
    with uow.transaction() as session:
        yield uow


@pytest.fixture(scope="function", autouse=True)
def create_tables(uow: UOW):
    uow.drop_all()
    uow.create_all()
