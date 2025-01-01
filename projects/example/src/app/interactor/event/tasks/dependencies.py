from collections.abc import Generator

from hexrepo_db import UOW
from hexrepo_task import SqsQueueAdapter, QueueAdapter
from hexrepo_task.adaptor.db import DynamoUOW


def get_queue_uow() -> Generator[UOW, None, None]:
    uow: UOW = DynamoUOW()
    yield uow


def get_task_queue() -> Generator[QueueAdapter, None, None]:
    queue = SqsQueueAdapter(queue="hexrepo-tasks")
    yield queue
