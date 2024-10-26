import os
from collections.abc import Generator

from app.adaptor.db.interface import UOW
from app.adaptor.db.sql import SqlUOW

DB_URL = os.environ["DB_URL"]


def get_uow() -> Generator[UOW, None, None]:
    uow = SqlUOW(db_url=DB_URL)
    with uow.transaction():
        yield uow
