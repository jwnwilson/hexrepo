import logging
import os
import sys

from pydantic_settings import BaseSettings

logger = logging.getLogger()


class Config(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    ENVIRONMENT: str = os.environ.get("environment", "dev")

    # Database settings
    READ_REPLICA_ENABLED: bool = (
        os.environ.get("READ_REPLICA_ENABLED", "false") == "true"
    )
    DB_URL: str = os.environ.get("DB_URL", "")
    DB_RO_URL: str = os.environ.get("DB_RO_URL", "")

    @property
    def DB_PASSWORD_SECRET_NAME(self) -> str:
        return os.environ.get("DB_PASSWORD_SECRET_NAME", "").format(
            env=self.ENVIRONMENT
        )

    DB_SQL_LOGGING: bool = os.environ.get("DB_SQL_LOGGING", "false") == "true"
    DB_SSL_CONNECTION: bool = os.environ.get("DB_SSL_CONNECTION", "false") == "true"
    CLOUD_PROVIDER: str = os.environ.get("CLOUD_PROVIDER", "local")
    TESTING: bool = "pytest" in sys.argv[0]


config = Config()
