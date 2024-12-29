from collections.abc import Generator

from hexrepo_db import UOW
from hexrepo_db.sql import get_sql_db_url

from app.adaptor.db.sql import SqlUOW


def get_uow() -> Generator[UOW, None, None]:
    uow = SqlUOW(db_url=get_sql_db_url())
    with uow.transaction():
        yield uow
