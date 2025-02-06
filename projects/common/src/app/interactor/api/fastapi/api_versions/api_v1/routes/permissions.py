from app.domain.user import PermissionDTO
from hexrepo_api import CrudRouter

from ......dependencies import get_uow, get_current_user

router_v1 = CrudRouter(
    db_dependency=get_uow,
    auth_adaptor=get_current_user,
    repository="permission",
    methods=["CREATE", "READ", "UPDATE", "DELETE"],
    response_schema=PermissionDTO,
    create_schema=PermissionDTO,
    update_schema=PermissionDTO,
)
