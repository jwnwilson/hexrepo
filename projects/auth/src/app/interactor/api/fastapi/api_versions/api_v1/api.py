from fastapi import APIRouter

from .routes.auth import router_v1 as auth_router
from .routes.healthcheck import router_v1 as healthcheck_router
from .routes.user import router_v1 as user_router

api_router_v1 = APIRouter()

api_router_v1.include_router(
    healthcheck_router,
    tags=["Healthcheck"],
    prefix="/healthcheck",
)
api_router_v1.include_router(
    auth_router,
    tags=["Auth"],
    prefix="/auth",
)
api_router_v1.include_router(
    user_router,
    tags=["User"],
    prefix="/user",
)
