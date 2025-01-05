from collections.abc import Generator

import pytest

from hexrepo_task.interface import QueueConfig, TaskUOW as UOW, QueueAdaptor
from hexrepo_task.adaptor.db import QueueUOW
from hexrepo_task.adaptor.queue.aws import SqsQueueAdaptor
from hexrepo_task.app import TaskApp


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
    TaskApp.task_registry = {}


@pytest.fixture
def queue() -> Generator[QueueAdaptor, None, None]:
    """
    Return db adaptor with initialised DB & DB session.
    """
    config: QueueConfig = QueueConfig(
        default_queue="test-queue",
        endpoint_url="http://localhost.localstack.cloud:4566"
    )
    queue = SqsQueueAdaptor(config)
    try:
        queue.delete_queue("test-queue")
    except Exception:
        pass
    queue.create_queue("test-queue")
    yield queue
