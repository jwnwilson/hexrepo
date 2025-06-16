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
    TRACING_ENABLED: bool = os.environ.get("TRACING_ENABLED", "false") == "true"


config: Config = Config()
