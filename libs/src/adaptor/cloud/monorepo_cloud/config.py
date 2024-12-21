import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

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
    AWS_REGION: str
    AWS_TF_STATE_BUCKET: str


config: Config = Config()


def load_aws_config() -> AWSConfig:
    try:
        return AWSConfig(
            AWS_REGION=os.environ["AWS_REGION"],
            AWS_ACCOUNT=os.environ["AWS_ACCOUNT"],
            AWS_TF_STATE_BUCKET=os.environ["AWS_TF_STATE_BUCKET"],
        )
    except KeyError:
        pass

    # Get config dir relatieve to this file
    script_path: Path = Path(os.path.realpath(__file__))
    config_path: str = str(
        script_path.parent.parent.parent.parent.parent / "config.json"
    )
    try:
        with open(config_path) as f:
            config: Dict[str, Any] = json.load(f)
    except FileNotFoundError:
        raise Exception(
            "Hexrepo config file not found: Please run `make setup` at project root to create config.json"
        )
    except json.JSONDecodeError as err:
        raise Exception("Hexrepo config file is not valid JSON: {err}")

    return AWSConfig(
        AWS_REGION=config["cloud_provider_config"]["AWS_REGION"],
        AWS_ACCOUNT=config["cloud_provider_config"]["AWS_ACCOUNT"],
        AWS_TF_STATE_BUCKET=config["cloud_provider_config"]["AWS_TF_STATE_BUCKET"],
    )
