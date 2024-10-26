from app.adaptor.db.sql.models.example import ExampleDTO

from ....crud import CrudRouter
from ....dependencies import get_uow


class CreateExampleDTO(ExampleDTO):
    pass


class UpdateExampleDTO(ExampleDTO):
    pass


router_v1 = CrudRouter(
    db_dependency=get_uow,
    respository="example",
    methods=["CREATE", "READ", "UPDATE", "DELETE"],
    response_schema=ExampleDTO,
    create_schema=CreateExampleDTO,
    update_schema=UpdateExampleDTO,
).router
