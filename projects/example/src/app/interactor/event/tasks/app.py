from hexrepo_task.app import TaskApp, TaskDTO, Dependency
from .dependencies import get_queue_uow, get_task_queue, get_uow
from app.adaptor.db.sql import SqlUOW


app = TaskApp(
    get_uow=get_queue_uow,
    get_queue=get_task_queue
)


@app.task
def create_example_task(task: TaskDTO, uow: SqlUOW = Dependency(get_uow)):
    uow.example.create(event.params)
