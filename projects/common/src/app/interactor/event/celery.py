from celery import Celery
from hexrepo_task.interactor.event.app import Dependency, resolve_dependencies
from hexrepo_task.interactor.event.celery import create_celery_app, CeleryConfig

from app.config import config
from app.adaptor.db.sql import SqlUOW
from app.domain.user import UserPermissionCreateDTO

from ..dependencies import get_uow

celery_config = CeleryConfig(
    CELERY_BROKER_URL=config.CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND=config.CELERY_RESULT_BACKEND,
    REGION=config.REGION,
)
celery_app: Celery = create_celery_app(celery_config)


@celery_app.task
def test_task():
    print("test task")


@celery_app.task()
@resolve_dependencies
def create_example_task(user_permissions: UserPermissionCreateDTO, uow: SqlUOW = Dependency(get_uow)):
    uow.user.create(user_permissions)

