from collections.abc import Generator

from fastapi import Depends
from hexrepo_db import UOW
from hexrepo_db.sql.config import get_sql_db_url
from hexrepo_task import QueueAdaptor, SqsQueueAdaptor, TaskAdaptor
from hexrepo_task.adaptor.db import QueueUOW
from hexrepo_task.interface import QueueConfig

from app.adaptor.db.sql import SqlUOW
from app.config import config


def get_queue_uow() -> Generator[UOW, None, None]:
    uow: UOW = QueueUOW(db_url=config.DB_QUEUE_URL)
    yield uow


def get_task_queue() -> Generator[QueueAdaptor, None, None]:
    queue_config: QueueConfig = QueueConfig(default_queue=config.TASK_QUEUE)
    queue = SqsQueueAdaptor(queue_config)
    yield queue


# Not sure hot to get this work for fastapi and also tasks
# Need to make Dependancy compatible with FastAPI
def get_task_adaptor(
    uow: UOW = Depends(get_queue_uow), queue: QueueAdaptor = Depends(get_task_queue)
) -> Generator[TaskAdaptor, None, None]:
    from app.interactor.event.tasks.app import task_app

    task_adaptor = TaskAdaptor(task_app, uow=uow, queue=queue)
    yield task_adaptor


def get_uow() -> Generator[UOW, None, None]:
    uow = SqlUOW(db_url=get_sql_db_url())
    with uow.transaction():
        yield uow
