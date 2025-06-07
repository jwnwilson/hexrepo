from uuid import UUID

from fastapi import Depends, HTTPException
from hexrepo_api import CrudRouter
from hexrepo_db.exception import RecordNotFound
from hexrepo_task import TaskAdaptor
from hexrepo_task.interface import TaskDTO

from app.adaptor.db.sql.models.example import ExampleDTO
from app.domain.example import CreateExampleDTO, UpdateExampleDTO
from app.interactor.event.tasks.app import create_example_task

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
def start_task(
    create_task: CreateExampleDTO, task_adaptor: TaskAdaptor = Depends(get_task_adaptor)
) -> TaskDTO:
    # Maybe we should have all tasks added to task_adaptor?
    # task_data: TaskDTO = task_adaptor.queue(
    #     create_example_task, params={"example": create_task}
    # ).task
    # Delay will use the api context
    async_result = create_example_task.delay(example=create_task)
    return async_result


@router_v1.router.get("/task/{id}")
def get_task(
    id: UUID, task_adaptor: TaskAdaptor = Depends(get_task_adaptor)
) -> TaskDTO:
    try:
        return task_adaptor.read(id)
    except RecordNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
