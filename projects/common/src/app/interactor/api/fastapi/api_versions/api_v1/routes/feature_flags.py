import json

from fastapi import Depends
from hexrepo_api import CrudRouter

from app.adaptor.db.interface import Repository
from app.domain.feature_flags import (
    FeatureFlagCreateDTO,
    FeatureFlagDTO,
    FeatureFlagGetDTO,
    FeatureFlagUpdateDTO,
    FlagsArgs,
    get_feature_flag_data,
)
from app.domain.user import UserPermissionDTO

from ......dependencies import (
    get_current_user,
    get_superadmin_user,
    get_uow,
    get_uow_ro,
)

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


@router_v1.get("/get_flags/", response_model=list[FeatureFlagGetDTO])
def get_feature_flags(
    flags: str = "[]",
    env: str = "dev",
    uow: Repository = Depends(get_uow_ro),
    user: UserPermissionDTO = Depends(get_current_user),
) -> list[FeatureFlagGetDTO]:
    flag_args = FlagsArgs(flags=json.loads(flags), env=env)
    return get_feature_flag_data(uow, flag_args)
