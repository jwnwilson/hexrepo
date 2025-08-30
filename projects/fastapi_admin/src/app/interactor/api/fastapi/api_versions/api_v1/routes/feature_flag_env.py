from hexrepo_api import CrudRouter

from app.domain.feature_flags import (
    FeatureFlagEnvCreateDTO,
    FeatureFlagEnvDTO,
    FeatureFlagEnvUpdateDTO,
)
from app.interactor.dependencies import (
    get_superadmin_user,
    get_uow,
    get_uow_ro,
)

router_v1 = CrudRouter(
    db_dependency=get_uow,
    db_dependency_ro=get_uow_ro,
    auth_adaptor=get_superadmin_user,
    repository="feature_flag_env",
    methods=["CREATE", "READ", "UPDATE", "DELETE"],
    response_schema=FeatureFlagEnvDTO,
    create_schema=FeatureFlagEnvCreateDTO,
    update_schema=FeatureFlagEnvUpdateDTO,
)
