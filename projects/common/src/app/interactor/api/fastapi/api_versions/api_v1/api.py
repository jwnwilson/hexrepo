from fastapi import APIRouter

from .routes.healthcheck import router_v1 as healthcheck_router
from .routes.users import router_v1 as users_router
from .routes.groups import router_v1 as groups_router
from .routes.permissions import router_v1 as permissions_router
from .routes.auth import router_v1 as auth_router

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
    auth_router,
    tags=["Auth"],
    prefix="/auth",
)
