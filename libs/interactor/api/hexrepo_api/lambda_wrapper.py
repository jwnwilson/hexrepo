import logging

from aws_xray_sdk.core import patch_all, xray_recorder
from mangum import Mangum

from .config import config


def create_lambda_handler(app):
    if config.TRACING_ENABLED:
        patch_all()

    # Initialize you log configuration using the base class
    logging.basicConfig(level=logging.INFO)
    logging.getLogger().setLevel(logging.INFO)

    @xray_recorder.capture("fastapi_request")
    def handler(event, context):
        if event.get("some-key"):
            # Do something or return, etc.
            return
        
        request_id: str = context.aws_request_id
        event["X-Request-ID"] = request_id

        asgi_handler = Mangum(app, lifespan="off")
        response = asgi_handler(
            event, context
        )  # Call the instance with the event arguments

        return response
    return handler
