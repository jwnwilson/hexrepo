from fastapi import APIRouter

from .routes.auth import router_v1 as auth_router
from .routes.company import router_v1 as company_router
from .routes.environments import router_v1 as environments_router
from .routes.feature_flag_env import router_v1 as feature_flag_env_router
from .routes.feature_flags import router_v1 as feature_flags_router
from .routes.groups import router_v1 as groups_router
from .routes.healthcheck import router_v1 as healthcheck_router
from .routes.permissions import router_v1 as permissions_router
from .routes.users import router_v1 as users_router

api_router_v1 = APIRouter()

api_router_v1.include_router(
    healthcheck_router,
    tags=["Healthcheck"],
    prefix="/healthcheck",
)

api_router_v1.include_router(
    users_router,
    tags=["Users"],
    prefix="/user",
)

api_router_v1.include_router(
    groups_router,
    tags=["Groups"],
    prefix="/group",
)

api_router_v1.include_router(
    permissions_router,
    tags=["Permissions"],
    prefix="/permission",
)

api_router_v1.include_router(
    feature_flags_router,
    tags=["Feature Flags"],
    prefix="/feature_flag",
)

api_router_v1.include_router(
    feature_flag_env_router,
    tags=["Feature Flag"],
    prefix="/feature_flag_env",
)

api_router_v1.include_router(
    company_router,
    tags=["Company"],
    prefix="/company",
)

api_router_v1.include_router(
    auth_router,
    tags=["Auth"],
    prefix="/auth",
)

api_router_v1.include_router(
    environments_router,
    tags=["Environments"],
    prefix="/environment",
)
