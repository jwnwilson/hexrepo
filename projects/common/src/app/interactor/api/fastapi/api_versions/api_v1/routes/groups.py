from hexrepo_api import CrudRouter

from app.domain.user import GroupPermissionDTO

from ......dependencies import get_current_user, get_uow, get_uow_ro

router_v1 = CrudRouter(
    db_dependency=get_uow,
    db_dependency_ro=get_uow_ro,
    auth_adaptor=get_current_user,
    repository="group",
    methods=["CREATE", "READ", "UPDATE", "DELETE"],
    response_schema=GroupPermissionDTO,
    create_schema=GroupPermissionDTO,
    update_schema=GroupPermissionDTO,
)
