import os

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from hexrepo_log import LogMiddleware, setup_logger
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

from app.config import config

from .admin import setup_admin
from .api_versions.api_v1.api import api_router_v1

ENVIRONMENT = os.environ.get("ENVIRONMENT", "")

setup_logger()


class RedirectMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if config.ORIGIN_URL and response.status_code in (301, 302, 303, 307, 308):
            # Workaround for AWS NLB redirecting to private DNS
            if response.headers.get("location"):
                url_path = response.headers["location"].split(request.url.netloc)[1]
                response.headers["location"] = config.ORIGIN_URL + url_path
            else:
                response.headers["location"] = config.ORIGIN_URL
        return response


root_prefix = ""

if config.SENTRY_DSN:
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
    )

app: FastAPI = FastAPI(
    title="Hexrepo Service",
    description="Hexrepo common service, for users, groups, auth and feature flags",
    version="0.0.1",
    root_path=root_prefix,
)


app.add_middleware(LogMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RedirectMiddleware)
# Sets all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=config.SESSION_SECRET, max_age=None)
app.include_router(api_router_v1, prefix="/api/v1")

setup_admin(app)


@app.get("/")
async def version():
    return {"message": "Hexrepo service"}
