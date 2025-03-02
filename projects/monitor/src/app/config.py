import logging
import os

from pydantic_settings import BaseSettings

logger = logging.getLogger()
# Silence noisy logs from faker
logging.getLogger("faker.factory").setLevel(logging.ERROR)


class Config(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    # Current environment
    CLOUD_PROVIDER: str = os.environ.get("CLOUD_PROVIDER", "local")
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "dev")

    # FEATURE FLAGS

    # Database settings
    DB_PASSWORD_SECRET_NAME: str = os.environ.get("DB_PASSWORD_SECRET_NAME", "").format(env=ENVIRONMENT)
    DB_URL: str = os.environ["DB_URL"]

    DB_SQL_LOGGING: bool = os.environ.get("DB_SQL_LOGGING", "false") == "true"
    DB_SSL_CONNECTION: bool = os.environ.get("DB_SSL_CONNECTION", "false") == "true"

    # API settings
    API_PREFIX: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000

    ALLOWED_ORIGINS: str = os.environ.get("ALLOWED_ORIGINS", "localhost")


config = Config()  # type: ignore
