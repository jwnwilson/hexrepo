from collections.abc import Generator

import pytest

from hexrepo_task.interface import QueueConfig, TaskUOW as UOW, QueueAdapter
from hexrepo_task.adaptor.db import QueueUOW
from hexrepo_task.adaptor.queue.aws import SqsQueueAdapter
from hexrepo_task.app import Task


@pytest.fixture
def uow() -> Generator[UOW, None, None]:
    """
    Return db adaptor with initialised DB & DB session.
    """
    uow = QueueUOW(db_url="http://localhost.localstack.cloud:4566")
    # Create DB session
    yield uow


@pytest.fixture(scope="function", autouse=True)
def create_tables(uow: UOW):
    uow.drop_all()
    uow.create_all()


@pytest.fixture(scope="function", autouse=True)
def clear_task_registry():
    Task.task_registry = {}


@pytest.fixture
def queue() -> Generator[QueueAdapter, None, None]:
    """
    Return db adaptor with initialised DB & DB session.
    """
    config: QueueConfig = QueueConfig(
        queue="test-queue",
        endpoint_url="http://localhost.localstack.cloud:4566"
    )
    queue = SqsQueueAdapter(config)
    try:
        queue.delete_queue("test-queue")
    except Exception:
        pass
    queue.create_queue("test-queue")
    yield queue
