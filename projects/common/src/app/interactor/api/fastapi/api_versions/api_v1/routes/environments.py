from hexrepo_api import CrudRouter

from app.domain.user import EnvironmentCreateDTO, EnvironmentDTO

from ......dependencies import get_superadmin_user, get_uow, get_uow_ro

router_v1 = CrudRouter(
    db_dependency=get_uow,
    db_dependency_ro=get_uow_ro,
    auth_adaptor=get_superadmin_user,
    repository="environment",
    methods=["CREATE", "READ", "UPDATE", "DELETE"],
    response_schema=EnvironmentDTO,
    create_schema=EnvironmentCreateDTO,
    update_schema=EnvironmentDTO,
)
