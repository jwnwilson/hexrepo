from hexrepo_task.interactor.event.app import Dependency, TaskApp, TaskDTO
from projects.auth.src.app.domain.user import ExampleDTO

from app.adaptor.db.sql import SqlUOW

from ...dependencies import get_queue_uow, get_task_queue, get_uow

app = TaskApp(get_uow=get_queue_uow, get_queue=get_task_queue)


@app.task
def create_example_task(task: TaskDTO, uow: SqlUOW = Dependency(get_uow)):
    example_dto: ExampleDTO = ExampleDTO(**task.params)
    uow.example.create(example_dto)
