import logging
from typing import Any

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
        if "headers" not in event:
            event["headers"] = {}
        if "X-Request-ID" not in event["headers"]:
            event["headers"]["X-Request-ID"] = context.aws_request_id
        
        # Handle scheduled events
        if "detail-type" in event and event["detail-type"] == "Scheduled Event":
            return {
                "statusCode": 200,
                "body": "Scheduled event processed"
            }

        asgi_handler = Mangum(app, lifespan="off")
        response = asgi_handler(
            event, context
        )  # Call the instance with the event arguments

        return response

    return handler
