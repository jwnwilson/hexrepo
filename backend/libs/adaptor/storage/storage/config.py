import os
import logging
from pydantic_settings import BaseSettings

logger = logging.getLogger()


class Config(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """
    # Current environment
    environment: str = os.environ.get("environment", "dev") 

    # AWS storage config
    AWS_DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION", "eu-west-1")


config = Config()  # type: ignore