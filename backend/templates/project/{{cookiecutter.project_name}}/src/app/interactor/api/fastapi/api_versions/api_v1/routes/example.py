from typing import Optional
from pydantic import BaseModel
from app.adaptor.db.sql.models.example import ExampleDTO

from ....crud import CrudRouter
from ....dependencies import get_uow


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
