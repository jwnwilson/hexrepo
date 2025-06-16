from typing import Optional
from uuid import UUID

from fastapi import Depends
from hexrepo_api import CrudRouter
from hexrepo_task.adaptor.db import QueueUOW
from hexrepo_task.interface import TaskDTO
from pydantic import BaseModel

from app.domain.example import ExampleDTO
from app.interactor.event.tasks.serverless_tasks import example_task

from ......dependencies import get_queue_uow, get_uow


class CreateExampleDTO(BaseModel):
    name: str
    url: str
    location: str


class UpdateExampleDTO(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    location: Optional[str] = None


router_v1 = CrudRouter(
    db_dependency=get_uow,
    repository="example",
    methods=["CREATE", "READ", "UPDATE", "DELETE"],
    response_schema=ExampleDTO,
    create_schema=CreateExampleDTO,
    update_schema=UpdateExampleDTO,
)


@router_v1.router.post("/task")
def start_task():
    example: ExampleDTO = ExampleDTO(
        name="example", url="example.com", location="example"
    )
    example_task.delay(params=example)
    return 204


@router_v1.router.get("/task")
def get_task(id: UUID, task_db: QueueUOW = Depends(get_queue_uow)) -> TaskDTO:
    return task_db.task.read(id)

