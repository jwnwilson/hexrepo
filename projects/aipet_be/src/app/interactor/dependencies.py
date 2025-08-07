import logging
import uuid
from collections.abc import Generator
from pydantic import BaseModel

from app.config import config
from hexrepo_task.interface import QueueConfig


from hexrepo_db import UOW


from hexrepo_db.sql import get_sql_db_url
from app.adaptor.db.sql import SqlUOW


logger = logging.getLogger(__name__)



def get_uow() -> Generator[UOW, None, None]:
    uow = SqlUOW(db_url=get_sql_db_url())
    with uow.transaction():
        yield uow


