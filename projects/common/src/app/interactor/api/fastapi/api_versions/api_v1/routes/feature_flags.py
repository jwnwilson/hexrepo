from hexrepo_api import CrudRouter

from app.domain.user import FeatureFlagDTO

from ......dependencies import get_current_user, get_uow, get_uow_ro

router_v1 = CrudRouter(
    db_dependency=get_uow,
    db_dependency_ro=get_uow_ro,
    auth_adaptor=get_current_user,
    repository="feature_flag",
    methods=["CREATE", "READ", "UPDATE", "DELETE"],
    response_schema=FeatureFlagDTO,
    create_schema=FeatureFlagDTO,
    update_schema=FeatureFlagDTO,
)
