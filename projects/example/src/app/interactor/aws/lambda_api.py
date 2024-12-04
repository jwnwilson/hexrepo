import logging

from mangum import Mangum

# Initialize you log configuration using the base class
logging.basicConfig(level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)

from ..api.fastapi.main import app

# To plug into lambda
handler = Mangum(app)
