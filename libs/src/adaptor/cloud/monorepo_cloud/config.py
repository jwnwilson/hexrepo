import os
import logging
from typing import Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings

logger = logging.getLogger()


class Config(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """
    environment: str = os.environ.get("ENVIRONMENT", "dev")    


class AWSConfig(BaseModel):
    AWS_ACCOUNT: str
    AWS_DEFAULT_REGION: str
    AWS_TF_STATE_BUCKET: str


config = Config()  # type: ignore