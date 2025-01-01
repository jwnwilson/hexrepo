from collections.abc import Generator

from hexrepo_db import UOW
from hexrepo_db.sql.config import get_sql_db_url
from hexrepo_task import SqsQueueAdapter, QueueAdapter
from hexrepo_task.adaptor.db import DynamoUOW
from app.adaptor.db.sql import SqlUOW


def get_queue_uow() -> Generator[UOW, None, None]:
    uow: UOW = DynamoUOW()
    yield uow


def get_task_queue() -> Generator[QueueAdapter, None, None]:
    queue = SqsQueueAdapter(queue="hexrepo-tasks")
    yield queue


def get_uow() -> Generator[UOW, None, None]:
    uow = SqlUOW(db_url=get_sql_db_url())
    with uow.transaction():
        yield uow
