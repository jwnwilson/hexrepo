import os

from app.config import config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .api_versions.api_v1.api import api_router_v1

ENVIRONMENT = os.environ.get("ENVIRONMENT", "")

root_prefix = ""

app = FastAPI(
    title="nosql Service",
    description="nosql description",
    version="0.0.1",
    root_path=root_prefix,
)

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


@app.get("/")
async def version():
    return {"message": "nosql service"}
