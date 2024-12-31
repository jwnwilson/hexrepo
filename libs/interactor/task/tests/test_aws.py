from hexrepo_db.nosql.dynamo.models.example import DynamoUOW
from hexrepo_task.app import TaskApp, TaskPromise
from hexrepo_task.adaptor.queue.aws import SqsQueueAdapter
from hexrepo_task.interface import TaskDTO


def test_aws_queue_task(uow: DynamoUOW, queue: SqsQueueAdapter):
    breakpoint()
    app = TaskApp(
        uow=uow,
        queue=queue
    )

    @app.task
    def task_A(event: TaskDTO):
        return "result"

    # run task directly
    task_result = task_A(name="example", status="running")

    assert task_result == "result"

    # queue task
    task_queue_instance: TaskPromise = task_A.queue()

    assert task_queue_instance.task.state.status == "pending"


def test_aws_handle_task(uow: DynamoUOW, queue: SqsQueueAdapter):
    breakpoint()
    app = TaskApp(
        uow=DynamoUOW(),
        queue=SqsQueueAdapter()
    )

    @app.task
    def task_A(event: TaskDTO):
        return "result"

    # queue task
    task_queue_instance: TaskPromise = task_A.queue()

    

    task_queue_instance.wait()

    assert task_queue_instance.task.state.status == "completed"

