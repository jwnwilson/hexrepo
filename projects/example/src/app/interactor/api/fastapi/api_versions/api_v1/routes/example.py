from uuid import UUID

from fastapi import Depends
from hexrepo_api import CrudRouter
from hexrepo_task import TaskAdaptor
from hexrepo_task.interface import TaskCreateDTO, TaskDTO

from app.adaptor.db.sql.models.example import ExampleDTO
from app.domain.example import CreateExampleDTO, UpdateExampleDTO

from ......dependencies import get_task_adaptor, get_uow

router_v1 = CrudRouter(
    db_dependency=get_uow,
    repository="example",
    methods=["CREATE", "READ", "UPDATE", "DELETE"],
    response_schema=ExampleDTO,
    create_schema=CreateExampleDTO,
    update_schema=UpdateExampleDTO,
)


@router_v1.router.post("/task")
def start_task(task_adaptor: TaskAdaptor = Depends(get_task_adaptor)) -> int:
    params: CreateExampleDTO = CreateExampleDTO(
        name="example", url="example.com", location="example"
    )
    task_data: TaskCreateDTO = TaskCreateDTO(
        name="create_example_task", 
        params=params.model_dump()
    )
    task_adaptor.queue(task_data)
    return 204


@router_v1.router.get("/task")
def get_task(id: UUID, task_adaptor: TaskAdaptor = Depends(get_task_adaptor)) -> TaskDTO:
    return task_adaptor.read(id)
