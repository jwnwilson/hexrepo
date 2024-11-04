import os
from collections.abc import Generator

from app.adaptor.db.interface import UOW
from app.adaptor.db.sql import SqlUOW
from app.config import config


def get_uow() -> Generator[UOW, None, None]:
    uow = SqlUOW(db_url=config.DB_URL)
    with uow.transaction():
        yield uow
