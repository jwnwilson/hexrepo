from app.domain.user import FeatureFlagDTO
from hexrepo_api import CrudRouter

from ......dependencies import get_uow, get_current_user

router_v1 = CrudRouter(
    db_dependency=get_uow,
    auth_adaptor=get_current_user,
    repository="feature_flag",
    methods=["CREATE", "READ", "UPDATE", "DELETE"],
    response_schema=FeatureFlagDTO,
    create_schema=FeatureFlagDTO,
    update_schema=FeatureFlagDTO,
)
