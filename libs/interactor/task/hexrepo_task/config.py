import logging
import os

from pydantic_settings import BaseSettings

logger = logging.getLogger()
# Silence noisy logs from faker
logging.getLogger("faker.factory").setLevel(logging.ERROR)


class TaskConfig(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    # Current environment
    PROJECT: str = os.environ.get("PROJECT", "hexrepo")
    CLOUD_PROVIDER: str = os.environ.get("CLOUD_PROVIDER", "aws")
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "dev")
    REGION: str = os.environ.get("REGION", "eu-west-1")

    # Database settings


config = TaskConfig()  # type: ignore
