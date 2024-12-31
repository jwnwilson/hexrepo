from collections.abc import Generator

import pytest

from hexrepo_task.interface import TaskUOW as UOW, QueueAdapter
from hexrepo_task.adaptor.db.nosql import DynamoUOW
from hexrepo_task.adaptor.queue.aws import SqsQueueAdapter


@pytest.fixture
def uow() -> Generator[UOW, None, None]:
    """
    Return db adaptor with initialised DB & DB session.
    """
    breakpoint()
    uow = DynamoUOW(db_url="http://localhost.localstack.cloud:4566")
    # Create DB session
    yield uow


@pytest.fixture(scope="function", autouse=True)
def create_tables(uow: UOW):
    uow.drop_all()
    uow.create_all()


@pytest.fixture
def queue() -> Generator[QueueAdapter, None, None]:
    """
    Return db adaptor with initialised DB & DB session.
    """
    breakpoint()
    queue = SqsQueueAdapter(queue_url="http://localhost.localstack.cloud:4566")
    queue.delete_queue("test-queue")
    queue.create_queue("test-queue")
    yield queue
