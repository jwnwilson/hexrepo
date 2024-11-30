import logging
import os
from typing import Optional

from pydantic_settings import BaseSettings

logger = logging.getLogger()


class Config(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    environment: str = os.environ.get("environment", "dev")


config: Config = Config()
