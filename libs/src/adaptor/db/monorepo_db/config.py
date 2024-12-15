import logging
import os

from pydantic_settings import BaseSettings

logger = logging.getLogger()


class Config(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    environment: str = os.environ.get("environment", "dev")

    # Database settings
    DB_URL: str = os.environ["DB_URL"]
    DB_SQL_LOGGING: bool = os.environ.get("DB_SQL_LOGGING", "false") == "true"
    DB_SSL_CONNECTION: bool = os.environ.get("DB_SSL_CONNECTION", "false") == "true"
    CLOUD_PROVIDER: str = os.environ.get("CLOUD_PROVIDER", "local")


config = Config()
