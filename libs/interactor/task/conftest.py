from collections.abc import Generator

from celery import Celery
import pytest

from hexrepo_task.config import TaskConfig
from hexrepo_task.interface import QueueConfig, TaskUOW as UOW, QueueAdaptor
from hexrepo_task.adaptor.db import QueueUOW
from hexrepo_task.adaptor.queue.aws import SqsQueueAdaptor
from hexrepo_task.interactor.event.celery import celery_app
from hexrepo_task.config import config


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


@pytest.fixture
def task_app(queue: QueueAdaptor) -> Generator[Celery, None, None]:
    task_config: TaskConfig = TaskConfig(
        queues={"test-queue": queue.get_queue_url("test-queue")},
        backend_table=f"{config.project}_{config.environment}_tasks",
        queue_endpoint=f"http://sqs.{config.region}.localhost.localstack.cloud:4566",
        backend_endpoint="http://localhost.localstack.cloud:4566",
    )
    task_app = celery_app(task_config)
    return task_app
