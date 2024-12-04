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
    public_url_timeout: int = 3600

    # AWS storage config
    aws_default_region: Optional[str] = os.environ.get(
        "AWS_DEFAULT_REGION", "eu-west-1"
    )


config: Config = Config()
