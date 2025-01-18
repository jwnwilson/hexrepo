import logging

from hexrepo_task.interactor.event.app import Dependency, TaskApp, TaskDTO

from app.adaptor.db.sql import SqlUOW
from app.domain.example import CreateExampleDTO

from ...dependencies import get_queue_uow, get_task_queue, get_uow

logger = logging.getLogger(__name__)


task_app = TaskApp(get_uow=get_queue_uow, get_queue=get_task_queue)


@task_app.task
def create_example_task(example: CreateExampleDTO, uow: SqlUOW = Dependency(get_uow)):
    logger.info(f"Creating example: {example}")
    uow.example.create(example)
