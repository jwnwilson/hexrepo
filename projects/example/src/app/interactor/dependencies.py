from collections.abc import Generator

from hexrepo_db import UOW
from hexrepo_db.sql.config import get_sql_db_url
from hexrepo_task import QueueAdaptor, SqsQueueAdaptor, TaskAdaptor
from hexrepo_task.adaptor.db import QueueUOW
from hexrepo_task.app import Dependency

from app.adaptor.db.sql import SqlUOW
from app.interactor.event.tasks.app import app



def get_queue_uow() -> Generator[UOW, None, None]:
    uow: UOW = QueueUOW()
    yield uow


def get_task_queue() -> Generator[QueueAdaptor, None, None]:
    queue = SqsQueueAdaptor(queue="hexrepo-tasks")
    yield queue


# Not sure hot to get this work for fastapi and also tasks
def get_task_adaptor(
    uow: UOW = Dependency(get_queue_uow),
    queue: QueueAdaptor= Dependency(get_queue_uow)
) -> Generator[TaskAdaptor, None, None]:
    task_adaptor = TaskAdaptor(app, uow=uow, queue=queue)
    yield task_adaptor


def get_uow() -> Generator[UOW, None, None]:
    uow = SqlUOW(db_url=get_sql_db_url())
    with uow.transaction():
        yield uow
