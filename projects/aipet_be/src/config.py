import logging
import os
import sys
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

logger = logging.getLogger()
# Silence noisy logs from faker
logging.getLogger("faker.factory").setLevel(logging.ERROR)

ENV = os.environ.get("ENVIRONMENT", "local")
env_file: str = os.environ.get("ENV_FILE", f"./env/{ENV}.env")
logger.info(f"Loading environment variables from : {env_file}")
load_dotenv(env_file)


class Config(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    # Current environment
    PROJECT: str = os.environ.get("PROJECT", "aipet_be")
    CLOUD_PROVIDER: str = os.environ.get("CLOUD_PROVIDER", "local")
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "dev")
    REGION: str = os.environ.get("REGION", "eu-west-1")
    SENTRY_DSN: Optional[str] = os.environ.get("SENTRY_DSN")

    # Auth settings
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "")
    SESSION_SECRET: str = os.environ.get("SESSION_SECRET", "")

    # FEATURE FLAGS

    TASK_QUEUE: str = os.environ.get("TASK_QUEUE", "aipet_be-tasks")

    # Database settings
    DB_PASSWORD_SECRET_NAME: str = os.environ.get("DB_PASSWORD_SECRET_NAME", "").format(
        env=ENVIRONMENT
    )
    DB_URL: str = os.environ["DB_URL"]

    DB_SQL_LOGGING: bool = os.environ.get("DB_SQL_LOGGING", "false") == "true"
    DB_SSL_CONNECTION: bool = os.environ.get("DB_SSL_CONNECTION", "false") == "true"

    # API settings
    API_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    ALLOWED_ORIGINS: str = os.environ.get("ALLOWED_ORIGINS", "localhost")
    TESTING: bool = "pytest" in sys.argv[0]

    # OpenRouter settings
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    AI_DEFAULT_MODEL: str = os.environ.get("AI_DEFAULT_MODEL", "anthropic/claude-3.5-sonnet")
    AI_TIMEOUT: int = int(os.environ.get("AI_TIMEOUT", "30"))


config = Config()  # type: ignore
