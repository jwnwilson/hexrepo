from app.interactor.event.tasks.app import create_example_task
from app.adaptor.db.sql import SqlUOW

from hexrepo_task.app import TaskApp, TaskPromise
from hexrepo_task.interface import QueueAdaptor


def test_example_event_create_example_task(
        task_client: TaskApp, queue: QueueAdaptor, uow: SqlUOW
):
    task_promise: TaskPromise = task_client.queue_task(
        create_example_task,
        # Can we use a DTO here?
        params={
            "name": "test_01", 
            "url": "https://test.com",
            "location": "test location"
        }
    ) 
    assert uow.example.read_multi().total == 0

    with queue.get_task() as task_event:
        assert task_event is not None
        task_client.handle(task_event)
    
    task_promise.wait()
    assert uow.example.read_multi().total == 1
    assert task_promise.task.status == "completed"
