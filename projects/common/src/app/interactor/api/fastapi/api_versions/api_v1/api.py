from fastapi import APIRouter

from .routes.healthcheck import router_v1 as healthcheck_router
from .routes.users import router_v1 as users_router
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
    auth_router,
    tags=["Auth"],
    prefix="/auth",
)
