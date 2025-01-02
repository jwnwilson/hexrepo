import logging
from hexrepo_task.app import Dependency, TaskApp, TaskDTO

from app.adaptor.db.sql import SqlUOW
from app.domain.example import ExampleDTO

from ...dependencies import get_queue_uow, get_task_queue, get_uow

logger = logging.getLogger(__name__)


app = TaskApp(get_uow=get_queue_uow, get_queue=get_task_queue)


@app.task
def create_example_task(task: TaskDTO, uow: SqlUOW = Dependency(get_uow)):
    logger.info(f"Creating example: {task.params}")
    example_dto: ExampleDTO = ExampleDTO(**task.params)
    uow.example.create(example_dto)
