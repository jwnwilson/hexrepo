import logging
from collections.abc import Generator

from hexrepo_db import UOW
from hexrepo_db.sql import get_sql_db_url
from hexrepo_task import QueueAdaptor, SqsQueueAdaptor
from hexrepo_task.adaptor.db import QueueUOW
from hexrepo_task.interface import QueueConfig

from app.adaptor.db.sql import SqlUOW
from app.config import config

logger = logging.getLogger(__name__)



def get_uow() -> Generator[UOW, None, None]:
    uow = SqlUOW(db_url=get_sql_db_url())
    with uow.transaction():
        yield uow



def get_queue_uow() -> Generator[UOW, None, None]:
    uow: UOW = QueueUOW()
    yield uow


def get_task_queue() -> Generator[QueueAdaptor, None, None]:
    queue_config: QueueConfig = QueueConfig(default_queue=config.TASK_QUEUE)
    queue = SqsQueueAdaptor(config=queue_config)
    yield queue
