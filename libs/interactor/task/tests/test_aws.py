from typing import Tuple
from uuid import uuid4

from fastapi import Depends
import pytest

from hexrepo_task.adaptor.queue.aws import SqsQueueAdaptor
from hexrepo_task.exception import DuplicateTaskName
from hexrepo_task.interactor.event.app import (
    Dependency,
    TaskApp,
    TaskFuncWrapper,
    TaskPromise,
)
from hexrepo_task.interface import TaskDTO

TaskAppValues = Tuple[TaskApp, TaskFuncWrapper]


@pytest.fixture
def task_A(task_app: TaskApp) -> TaskAppValues:
    @task_app.task
    def task_A(task: TaskDTO):
        return task.params["name"]

    return task_app, task_A


def test_invalid_task_name(task_app: TaskApp):
    with pytest.raises(ValueError):

        @task_app.task
        def task_A_invalid(event: TaskDTO):
            return event.params["name"]


def test_duplicate_task(task_A: TaskAppValues):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = task_A

    with pytest.raises(DuplicateTaskName):
        # Duplicate task
        @app.task
        def task_A(event: TaskDTO):
            return event.params["name"]


def test_aws_queue_task(task_A: TaskAppValues, queue: SqsQueueAdaptor):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = task_A

    test_event = TaskDTO(
        name="task_A", params=dict(name="example", status="running"), id=uuid4()
    )
    # run task directly
    task_result = task_A(test_event)
    assert task_result == "example"
    # queue task
    task_queue_instance: TaskPromise = app.queue_task(
        task_A, params=dict(name="example", status="running")
    )
    assert task_queue_instance.task.status == "queued"
    # get task
    with queue.get_task() as event:
        assert event.id == task_queue_instance.task.id


def test_aws_handle_task(task_A: TaskAppValues, queue: SqsQueueAdaptor):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = task_A

    # queue task
    task_queue_instance: TaskPromise = app.queue_task(
        task_A, params=dict(name="example", status="running")
    )
    # get task
    with queue.get_task() as event:
        # handle task
        result = app.handle(event)
        assert result == "example"

    # Assert task updated
    task_queue_instance.wait()
    assert task_queue_instance.task.status == "completed"


def test_aws_queue_multiple_task(task_A: TaskAppValues, queue: SqsQueueAdaptor):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = task_A

    # queue task
    task_queue_instance_01: TaskPromise = app.queue_task(
        task_A, params=dict(name="example", status="running")
    )
    task_queue_instance_02: TaskPromise = app.queue_task(
        task_A, params=dict(name="example", status="running")
    )
    task_ids = [
        task_queue_instance_01.task.id,
        task_queue_instance_02.task.id,
    ]
    # get task
    with queue.get_task() as task_01:
        assert task_01.id in task_ids
    with queue.get_task() as task_02:
        assert task_02.id in task_ids
    with queue.get_task() as no_task:
        assert no_task is None


def test_aws_task_error_handled(task_A, queue: SqsQueueAdaptor):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = task_A

    @app.task
    def task_A_error(task: TaskDTO):
        raise Exception("error")

    # queue task
    task_queue_instance: TaskPromise = app.queue_task(
        task_A_error, params=dict(name="example", status="running")
    )
    # get task
    with queue.get_task() as event:
        # handle task
        with pytest.raises(Exception):
            app.handle(event)

    # Assert task updated
    task_queue_instance.wait()
    assert task_queue_instance.task.status == "error"


def test_aws_task_dependency(task_A, queue: SqsQueueAdaptor):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = task_A

    def get_test_str():
        return "dependency value"

    @app.task
    def task_A_dependency(task: TaskDTO, test: str = Dependency(get_test_str)):
        return test

    # queue task
    task_queue_instance: TaskPromise = app.queue_task(
        task_A_dependency, params=dict(name="example", status="running")
    )
    # get task
    with queue.get_task() as event:
        # handle task
        result = app.handle(event)
        assert result == "dependency value"

    # Assert task updated
    task_queue_instance.wait()
    assert task_queue_instance.task.status == "completed"


def test_aws_task_depends(task_A, queue: SqsQueueAdaptor):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = task_A

    def get_test_str():
        return "dependency value"

    @app.task
    def task_A_dependency(task: TaskDTO, test: str = Depends(get_test_str)):
        return test

    # queue task
    task_queue_instance: TaskPromise = app.queue_task(
        task_A_dependency, params=dict(name="example", status="running")
    )
    # get task
    with queue.get_task() as event:
        # handle task
        result = app.handle(event)
        assert result == "dependency value"

    # Assert task updated
    task_queue_instance.wait()
    assert task_queue_instance.task.status == "completed"
