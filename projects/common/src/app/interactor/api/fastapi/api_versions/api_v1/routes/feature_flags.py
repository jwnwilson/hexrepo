from hexrepo_api import CrudRouter

from app.domain.user import FeatureFlagCreateDTO, FeatureFlagDTO, FeatureFlagUpdateDTO

from ......dependencies import get_superadmin_user, get_uow, get_uow_ro

router_v1 = CrudRouter(
    db_dependency=get_uow,
    db_dependency_ro=get_uow_ro,
    auth_adaptor=get_superadmin_user,
    repository="feature_flag",
    methods=["CREATE", "READ", "UPDATE", "DELETE"],
    response_schema=FeatureFlagDTO,
    create_schema=FeatureFlagCreateDTO,
    update_schema=FeatureFlagUpdateDTO,
)
