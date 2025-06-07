from celery import Celery
from hexrepo_task.interactor.event.app import Dependency, TaskDTO
from hexrepo_task.interactor.event.celery_pydantic import pydantic_celery

from app.config import config
from app.adaptor.db.sql import SqlUOW
from app.domain.user import UserPermissionCreateDTO

from ..dependencies import get_uow

celery_app = Celery(
    "tasks", broker=config.CELERY_BROKER_URL, backend=config.CELERY_RESULT_BACKEND
)

pydantic_celery(celery_app)

celery_app.conf.broker_transport_options = {"region": config.REGION}


@celery_app.task
def test_task():
    print("test task")


@celery_app.task()
def create_example_task(task: TaskDTO, uow: SqlUOW = Dependency(get_uow)):
    from celery.contrib import rdb

    rdb.set_trace()
    user_dto: UserPermissionCreateDTO = UserPermissionCreateDTO(**task.params)
    uow.user.create(user_dto)


# from hexrepo_task.interactor.event.app import Dependency, TaskApp, TaskDTO

# from app.adaptor.db.sql import SqlUOW
# from app.domain.user import UserPermissionCreateDTO

# from ...dependencies import get_queue_uow, get_task_queue, get_uow

# # mode lambda / celery
# app = TaskApp(mode="celery", get_uow=get_queue_uow, get_queue=get_task_queue)


# # in celery mode return a celery task
# @app.task
# def create_example_task(task: TaskDTO, uow: SqlUOW = Dependency(get_uow)):
#     user_dto: UserPermissionCreateDTO = UserPermissionCreateDTO(**task.params)
#     uow.user.create(user_dto)
