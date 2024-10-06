from app.ports.db.model.property_model import PropteryDTO

from ....crud import CrudRouter
from ....dependencies import get_db


class CreatePropertyDTO(PropteryDTO):
    pass


class UpdatePropertyDTO(PropteryDTO):
    pass


router_v1 = CrudRouter(
    db_dependency=get_db,
    respository="example",
    methods=["CREATE", "READ", "UPDATE", "DELETE"],
    response_schema=PropteryDTO,
    create_schema=CreatePropertyDTO,
    update_schema=UpdatePropertyDTO,
).router
