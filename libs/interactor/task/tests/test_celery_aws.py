from typing import Callable, Dict
from uuid import uuid4

from celery import Celery
from celery.app.task import Task
import pytest

from hexrepo_db.interface import PaginatedData
from hexrepo_task.adaptor.queue.aws import SqsQueueAdaptor
from hexrepo_task.interface import UOW


@pytest.fixture
def task_A(task_app: Celery) -> Callable:

    @task_app.task
    def task_A(params: Dict):
        return params["name"]

    return task_A


def test_aws_queue_task(task_A: Task, queue: SqsQueueAdaptor, uow: UOW):
    # run task directly
    task_result: str = task_A({"name": "example"})
    assert task_result == "example"
    # queue task
    task_promise = task_A.delay({"name": "example"})
    # get task
    with queue.get_task() as event:
        assert task_promise.id == event["headers"]["id"]
    
    # Check result is in results backend
    task_results: PaginatedData = uow.task.read_multi()
    assert task_results.total > 0


def test_aws_handle_task(task_A, queue: SqsQueueAdaptor):
    # queue task
    task_promise = task_A.delay({"name": "example"})
    # get task
    with queue.get_task() as event:
        # handle task via lambda wrapper
        result = task_A(event)
        assert result == "example"
