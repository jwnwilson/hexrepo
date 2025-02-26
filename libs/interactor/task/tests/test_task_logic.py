from typing import Tuple
from unittest.mock import MagicMock, Mock

import pytest
from fastapi import Depends
from pydantic import BaseModel

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

    test_event = TaskDTO(name="task_A", params=dict(name="example", status="running"))
    # run task directly
    task_result = task_A(task=test_event)
    assert task_result == "example"
    # queue task
    task_queue_instance: TaskPromise = app.queue_task(
        task_A, params=dict(task=test_event)
    )
    assert task_queue_instance.task.status == "queued"
    # get task
    with queue.get_task() as event:
        assert event.id == task_queue_instance.task.id


def test_aws_handle_task(task_A: TaskAppValues, queue: SqsQueueAdaptor):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = task_A

    test_event = TaskDTO(name="task_A", params=dict(name="example", status="running"))
    # queue task
    task_queue_instance: TaskPromise = app.queue_task(
        task_A, params=dict(task=test_event)
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
    test_event = TaskDTO(name="task_A", params=dict(name="example", status="running"))
    task_queue_instance_01: TaskPromise = app.queue_task(
        task_A, params=dict(task=test_event)
    )
    task_queue_instance_02: TaskPromise = app.queue_task(
        task_A, params=dict(task=test_event)
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

    test_event = TaskDTO(name="task_A", params=dict(name="example", status="running"))
    # queue task
    task_queue_instance: TaskPromise = app.queue_task(
        task_A_error, params=dict(task=test_event)
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

    test_event = TaskDTO(name="task_A", params=dict(name="example", status="running"))
    # queue task
    task_queue_instance: TaskPromise = app.queue_task(
        task_A_dependency, params=dict(task=test_event)
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

    test_event = TaskDTO(name="task_A", params=dict(name="example", status="running"))
    # queue task
    task_queue_instance: TaskPromise = app.queue_task(
        task_A_dependency, params=dict(task=test_event)
    )
    # get task
    with queue.get_task() as event:
        # handle task
        result = app.handle(event)
        assert result == "dependency value"

    # Assert task updated
    task_queue_instance.wait()
    assert task_queue_instance.task.status == "completed"


def test_nested_dependency(task_A, queue: SqsQueueAdaptor):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = task_A

    def get_nested_test_str():
        return "nested dependency value"

    def get_test_str(test: str = Depends(get_nested_test_str)):
        return test

    @app.task
    def task_A_dependency(task: TaskDTO, test: str = Depends(get_test_str)):
        return test

    test_event = TaskDTO(name="task_A", params=dict(name="example", status="running"))
    # queue task
    task_queue_instance: TaskPromise = app.queue_task(
        task_A_dependency, params=dict(task=test_event)
    )
    # get task
    with queue.get_task() as event:
        # handle task
        result = app.handle(event)
        assert result == "nested dependency value"

    # Assert task updated
    task_queue_instance.wait()
    assert task_queue_instance.task.status == "completed"


def test_task_param_type_check(task_A: TaskAppValues, queue: SqsQueueAdaptor):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = task_A

    class TestPydantic(BaseModel):
        test: str

    @app.task
    def task_A_param_check(test_int: int, test_str: str, test_pydantic: TestPydantic):
        return {
            "test_int": test_int,
            "test_str": test_str,
            "test_pydantic": test_pydantic,
        }

    test_params = {
        "test_int": 1,
        "test_str": "test",
        "test_pydantic": TestPydantic(test="test"),
    }
    # Call task directly
    result = task_A_param_check(
        test_int=1, test_str="test", test_pydantic=TestPydantic(test="test")
    )
    assert result == test_params

    # Queue task
    task_queue_instance: TaskPromise = task_A_param_check.queue_task(**test_params)

    # get task
    with queue.get_task() as event:
        # handle task
        result = app.handle(event)
        assert result == test_params

    # Assert task updated
    task_queue_instance.wait()
    assert task_queue_instance.task.status == "completed"


def test_nested_cleanup_logic_called(task_A: TaskAppValues, queue: SqsQueueAdaptor):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = task_A
    cleanup_mock = Mock()

    def get_nested_test_str():
        yield "nested dependency value"
        cleanup_mock()

    def get_test_str(test: str = Depends(get_nested_test_str)):
        yield test
        cleanup_mock()

    @app.task
    def task_A_dependency(task: TaskDTO, test: str = Depends(get_test_str)):
        assert cleanup_mock.call_count == 0
        return test

    test_event = TaskDTO(name="task_A", params=dict(name="example", status="running"))
    # queue task
    task_queue_instance: TaskPromise = app.queue_task(
        task_A_dependency, params=dict(task=test_event)
    )
    # get task
    with queue.get_task() as event:
        # handle task
        result = app.handle(event)
        assert result == "nested dependency value"

    # Assert task updated
    task_queue_instance.wait()
    assert cleanup_mock.call_count == 2


@pytest.fixture
def mock_dependency_cache():
    cache_value = Dependency.cache
    Dependency.cache = MagicMock()
    Dependency.cache.__getitem__.side_effect = cache_value.__getitem__
    Dependency.cache.__contains__.side_effect = cache_value.__contains__
    yield cache_value
    Dependency.cache = cache_value


def test_task_cache_hit(
    task_A: TaskAppValues, queue: SqsQueueAdaptor, mock_dependency_cache
):
    app: TaskApp
    task_A: TaskFuncWrapper
    app, task_A = task_A
    cleanup_mock = Mock()

    def get_nested_test_str():
        yield "nested dependency value"
        cleanup_mock()

    def get_test_str_1(test: str = Depends(get_nested_test_str)):
        yield test
        cleanup_mock()

    def get_test_str_2(test: str = Depends(get_nested_test_str)):
        yield test
        cleanup_mock()

    # Set cache value for test
    mock_dependency_cache[get_nested_test_str] = "nested dependency value"

    @app.task
    def task_A_dependency(
        task: TaskDTO,
        test_1: str = Depends(get_test_str_1),
        test_2: str = Depends(get_test_str_2),
    ):
        assert cleanup_mock.call_count == 0
        return test_1, test_2

    test_event = TaskDTO(name="task_A", params=dict(name="example", status="running"))
    # queue task
    task_queue_instance: TaskPromise = app.queue_task(
        task_A_dependency, params=dict(task=test_event)
    )
    # get task
    with queue.get_task() as event:
        # handle task
        result = app.handle(event)
        assert result == ("nested dependency value", "nested dependency value")

    # Assert task updated
    task_queue_instance.wait()
    assert cleanup_mock.call_count == 2
    assert Dependency.cache.__getitem__.call_count == 2
