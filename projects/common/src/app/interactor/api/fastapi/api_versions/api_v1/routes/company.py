from hexrepo_api import CrudRouter

from app.domain.user import CompanyDTO, CompanyCreateDTO

from ......dependencies import get_superadmin_user, get_uow, get_uow_ro

router_v1 = CrudRouter(
    db_dependency=get_uow,
    db_dependency_ro=get_uow_ro,
    auth_adaptor=get_superadmin_user,
    repository="company",
    methods=["CREATE", "READ", "UPDATE", "DELETE"],
    response_schema=CompanyDTO,
    create_schema=CompanyCreateDTO,
    update_schema=CompanyDTO,
)
