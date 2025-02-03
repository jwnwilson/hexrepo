from app.domain.user import FeatureFlagDTO
from hexrepo_api import CrudRouter

from ......dependencies import get_uow

router_v1 = CrudRouter(
    db_dependency=get_uow,
    repository="feature_flag",
    methods=["CREATE", "READ", "UPDATE", "DELETE"],
    response_schema=FeatureFlagDTO,
    create_schema=FeatureFlagDTO,
    update_schema=FeatureFlagDTO,
)
