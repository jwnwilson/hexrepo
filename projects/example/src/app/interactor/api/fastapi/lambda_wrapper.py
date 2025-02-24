import logging

from mangum import Mangum
from aws_xray_sdk.core import xray_recorder, patch_all

patch_all()
# Initialize you log configuration using the base class
logging.basicConfig(level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)

from .main import app  # noqa

# To plug into lambda
# handler = Mangum(app, lifespan="off")

@xray_recorder.capture('fastapi_request')
def handler(event, context):
    if event.get("some-key"):
        # Do something or return, etc.
        return

    asgi_handler = Mangum(app, lifespan="off")
    response = asgi_handler(event, context) # Call the instance with the event arguments

    return response
