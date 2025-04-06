import logging
from typing import Any

from aws_xray_sdk.core import patch_all, xray_recorder
from mangum import Mangum

from .config import config


class ScheduledEventHandler:
    # Dummy handler to gracefully handle keep warm events
    @classmethod
    def infer(cls, event, context, config) -> bool:
        return "detail-type" in event and event["detail-type"] == "Scheduled Event"

    def __init__(self, event, context, config) -> None:
        self.event = event
        self.context = context
        self.config = config

    @property
    def body(self) -> bytes:
        return {}

    @property
    def scope(self):
        return {}

    def __call__(self, response) -> dict[str, Any]:
        return {
            "status": 200,
            "body": "Scheduled event processed"
        }



def create_lambda_handler(app):
    if config.TRACING_ENABLED:
        patch_all()

    # Initialize you log configuration using the base class
    logging.basicConfig(level=logging.INFO)
    logging.getLogger().setLevel(logging.INFO)

    @xray_recorder.capture("fastapi_request")
    def handler(event, context):
        print("Received event: %s", event)
        print("Received context: %s", context)
        
        request_id: str = context.aws_request_id
        event["headers"]["X-Request-ID"] = request_id

        asgi_handler = Mangum(app, lifespan="off", custom_handlers=[ScheduledEventHandler])
        response = asgi_handler(
            event, context
        )  # Call the instance with the event arguments

        return response

    return handler
