from typing import Optional
from uuid import UUID

from app.domain.example import CreateExampleDTO, UpdateExampleDTO
from fastapi import Depends
from hexrepo_api import CrudRouter
from hexrepo_task.adaptor.db import QueueUOW
from hexrepo_task.app import TaskApp
from hexrepo_task.interface import TaskDTO
from pydantic import BaseModel

from app.adaptor.db.sql.models.example import ExampleDTO
from app.interactor.event.tasks.app import create_example_task

from ......dependencies import get_queue_uow, get_uow

router_v1 = CrudRouter(
    db_dependency=get_uow,
    repository="example",
    methods=["CREATE", "READ", "UPDATE", "DELETE"],
    response_schema=ExampleDTO,
    create_schema=CreateExampleDTO,
    update_schema=UpdateExampleDTO,
)


@router_v1.router.post("/task")
def start_task(task_app: TaskApp = Depends(get_tasks)) -> int:
    params: CreateExampleDTO = CreateExampleDTO(
        name="example", url="example.com", location="example"
    )
    task_app.queue(create_example_task, params=params.model_dump())
    return 204


@router_v1.router.get("/task")
def get_task(id: UUID, task_app: TaskApp = Depends(get_tasks)) -> TaskDTO:
    return task_app.get_task(id)
