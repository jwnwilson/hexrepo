from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, APIRouter
from hexrepo_db.exception import RecordNotFound
from hexrepo_task import TaskAdaptor
from hexrepo_task.interactor.event.app import TaskPromise
from hexrepo_task.interface import TaskDTO

from app.interactor.event.tasks.serverless_tasks import create_example_task_serverless
from app.interactor.event.tasks.celery_tasks import create_example_task
from projects.common.src.app.domain.user import UserPermissionCreateDTO

from ......dependencies import get_task_adaptor, get_uow

router_v1 = APIRouter()


@router_v1.router.post("/task/celery")
def start_task_celery(
    user_permission: UserPermissionCreateDTO
) -> Any:
    async_result = create_example_task.delay(user_dto=user_permission)
    return async_result.task


@router_v1.router.post("/task/serverless")
def start_task_serverless(
    user_permission: UserPermissionCreateDTO
) -> TaskDTO:
    async_result: TaskPromise = create_example_task_serverless.delay(user_dto=user_permission)
    return async_result.task


@router_v1.router.get("/task/{id}")
def get_task(
    id: UUID, task_adaptor: TaskAdaptor = Depends(get_task_adaptor)
) -> TaskDTO:
    try:
        return task_adaptor.read(id)
    except RecordNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
