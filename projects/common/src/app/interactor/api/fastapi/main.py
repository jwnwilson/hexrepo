import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from hexrepo_log import LogMiddleware, setup_logger

from app.config import config
from .api_versions.api_v1.api import api_router_v1
from .admin import setup_admin

ENVIRONMENT = os.environ.get("ENVIRONMENT", "")

setup_logger()

root_prefix = f""

app: FastAPI = FastAPI(
    title="Hexrepo Service",
    description="Hexrepo common service, for users, groups, auth and feature flags",
    version="0.0.1",
    root_path=root_prefix,
)

app.add_middleware(LogMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
# Sets all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router_v1, prefix="/api/v1")

setup_admin(app)

@app.get("/")
async def version():
    return {"message": "Hexrepo service"}
