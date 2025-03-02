import logging

from aws_xray_sdk.core import patch_all, xray_recorder
from mangum import Mangum

from app.config import config

if config.TRACING_ENABLED:
    patch_all()

# Initialize you log configuration using the base class
logging.basicConfig(level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)

from .fastapi.main import app  # noqa


@xray_recorder.capture("fastapi_request")
def handler(event, context):
    if event.get("some-key"):
        # Do something or return, etc.
        return

    asgi_handler = Mangum(app, lifespan="off")
    response = asgi_handler(
        event, context
    )  # Call the instance with the event arguments

    return response
