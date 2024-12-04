from fastapi import APIRouter

from .routes.example import router_v1 as example_router
from .routes.healthcheck import router_v1 as healthcheck_router

api_router_v1 = APIRouter()

api_router_v1.include_router(
    healthcheck_router,
    tags=["Healthcheck"],
    prefix="/healthcheck",
)
api_router_v1.include_router(
    example_router,
    tags=["Example"],
    prefix="/example",
)
