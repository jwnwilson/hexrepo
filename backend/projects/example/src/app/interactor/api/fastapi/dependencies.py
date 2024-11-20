from collections.abc import Generator
from monorepo_db import UOW, get_db_url

from app.adaptor.db.sql import SqlUOW


def get_uow() -> Generator[UOW, None, None]:
    uow = SqlUOW(db_url=get_db_url())
    with uow.transaction():
        yield uow
