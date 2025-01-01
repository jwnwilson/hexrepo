from hexrepo_task.app import TaskApp, TaskDTO
from .dependencies import get_queue_uow, get_task_queue

app = TaskApp(get_uow=get_queue_uow, get_queue=get_task_queue)


@app.task
def example_task(event: TaskDTO):
    pass
