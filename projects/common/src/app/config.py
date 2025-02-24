import logging
import os
import sys

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

logger = logging.getLogger()
# Silence noisy logs from faker
logging.getLogger("faker.factory").setLevel(logging.ERROR)

load_dotenv(os.environ.get("ENV_FILE", "./env/local.env"))


class Config(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    # Current environment
    PROJECT: str = os.environ.get("PROJECT", "common")
    CLOUD_PROVIDER: str = os.environ.get("CLOUD_PROVIDER", "local")
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "dev")
    REGION: str = os.environ.get("REGION", "eu-west-1")

    # Auth settings
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "")
    SESSION_SECRET: str = os.environ["SESSION_SECRET"]
    # This needs to come from cognito
    CLIENT_ID: str = os.environ["CLIENT_ID"]
    USER_POOL_ID: str = os.environ["USER_POOL_ID"]

    # Database settings
    READ_REPLICA_ENABLED: bool = (
        os.environ.get("READ_REPLICA_ENABLED", "false") == "true"
    )
    DB_PASSWORD_SECRET_NAME: str = os.environ.get("DB_PASSWORD_SECRET_NAME", "")
    DB_URL: str = os.environ["DB_URL"]
    DB_RO_URL: str = os.environ.get("DB_RO_URL", "")

    DB_SQL_LOGGING: bool = os.environ.get("DB_SQL_LOGGING", "false") == "true"
    DB_SSL_CONNECTION: bool = os.environ.get("DB_SSL_CONNECTION", "false") == "true"

    # API settings
    API_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    ALLOWED_ORIGINS: str = os.environ.get("ALLOWED_ORIGINS", "localhost")
    TESTING: bool = "pytest" in sys.argv[0]


config = Config()  # type: ignore
