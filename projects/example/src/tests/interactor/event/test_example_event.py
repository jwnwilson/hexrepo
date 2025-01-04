from app.interactor.event.tasks.app import create_example_task

from hexrepo_task.app import TaskAdaptor, TaskApp, TaskPromise
from hexrepo_task.interface import QueueAdaptor


def test_example_event_create_example_task(task_client: TaskApp, queue: QueueAdaptor):
    task_promise: TaskPromise = task_client.queue_task(
        create_example_task,
        # Can we use a DTO here?
        params={
            "name": "test_01", 
            "url": "https://test.com",
            "location": "test location"
        }
    ) 
    with queue.get_task() as task_event:
        assert task_event is not None
        task_client.handle(task_event)
    
    task_promise.wait()
    assert task_promise.task.status == "completed"


        
    
