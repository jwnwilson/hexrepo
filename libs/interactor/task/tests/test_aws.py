from uuid import uuid4

import pytest
from hexrepo_db.nosql.dynamo.models.example import ExampleUOW

from hexrepo_task.adaptor.queue.aws import SqsQueueAdapter
from hexrepo_task.app import Dependency, TaskApp, TaskFuncWrapper, TaskPromise
from hexrepo_task.exception import DuplicateTaskName
from hexrepo_task.interface import TaskDTO


@pytest.fixture
def create_task_app(uow: ExampleUOW, queue: SqsQueueAdapter):
    def get_uow():
        return uow

    def get_queue():
        return queue

    app = TaskApp(get_uow=get_uow, get_queue=get_queue)

    @app.task
    def task_A(event: TaskDTO):
        return event.params["name"]

    return app, task_A


def test_duplicate_task(create_task_app):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = create_task_app

    with pytest.raises(DuplicateTaskName):
        # Duplicate task
        @app.task
        def task_A(event: TaskDTO):
            return event.params["name"]


def test_aws_queue_task(create_task_app, queue: SqsQueueAdapter):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = create_task_app

    test_event = TaskDTO(
        name="task_A", params=dict(name="example", status="running"), id=uuid4()
    )
    # run task directly
    task_result = task_A(test_event)
    assert task_result == "example"
    # queue task
    task_queue_instance: TaskPromise = task_A.queue()
    assert task_queue_instance.task.state.status == "queued"
    # get task
    with queue.get_task() as event:
        assert event.id == task_queue_instance.task.state.id


def test_aws_handle_task(create_task_app, queue: SqsQueueAdapter):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = create_task_app

    # queue task
    task_queue_instance: TaskPromise = task_A.queue(
        params=dict(name="example", status="running")
    )
    # get task
    with queue.get_task() as event:
        # handle task
        result = app.handle(event)
        assert result == "example"

    # Assert task updated
    task_queue_instance.wait()
    assert task_queue_instance.task.state.status == "completed"


def test_aws_queue_multiple_task(create_task_app, queue: SqsQueueAdapter):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = create_task_app

    # queue task
    task_queue_instance_01: TaskPromise = task_A.queue(
        params=dict(name="example", status="running")
    )
    task_queue_instance_02: TaskPromise = task_A.queue(
        params=dict(name="example", status="running")
    )
    task_ids = [
        task_queue_instance_01.task.state.id,
        task_queue_instance_02.task.state.id,
    ]
    # get task
    with queue.get_task() as task_01:
        assert task_01.id in task_ids
    with queue.get_task() as task_02:
        assert task_02.id in task_ids
    with queue.get_task() as no_task:
        assert no_task is None


def test_aws_task_error_handled(create_task_app, queue: SqsQueueAdapter):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = create_task_app

    @app.task
    def task_A_error(event: TaskDTO):
        raise Exception("error")

    # queue task
    task_queue_instance: TaskPromise = task_A_error.queue(
        params=dict(name="example", status="running")
    )
    # get task
    with queue.get_task() as event:
        # handle task
        with pytest.raises(Exception):
            app.handle(event)

    # Assert task updated
    task_queue_instance.wait()
    assert task_queue_instance.task.state.status == "error"


def test_aws_task_dependency(create_task_app, queue: SqsQueueAdapter):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = create_task_app

    def get_test_str():
        return "dependency value"

    @app.task
    def task_A_dependency(event: TaskDTO, test: str = Dependency(get_test_str)):
        return test

    # queue task
    task_queue_instance: TaskPromise = task_A_dependency.queue()
    # get task
    with queue.get_task() as event:
        # handle task
        result = app.handle(event)
        assert result == "dependency value"

    # Assert task updated
    task_queue_instance.wait()
    assert task_queue_instance.task.state.status == "completed"
