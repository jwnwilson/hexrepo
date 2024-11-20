import os
import logging
import json
from urllib.parse import quote 
from pydantic_settings import BaseSettings
from monorepo_storage.secrets.aws import AWSSecretAdaptor

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
    DB_PASSWORD_SECRET_NAME: str = os.environ.get("DB_PASSWORD_SECRET_NAME", "")
    DB_SQL_LOGGING: bool = os.environ.get("DB_SQL_LOGGING", "false") == "true"
    DB_SSL_CONNECTION: bool = os.environ.get("DB_SSL_CONNECTION", "false") == "true"  
    CLOUD_PROVIDER: str = os.environ.get("CLOUD_PROVIDER", "local")


config = Config()  # type: ignore


def get_db_url_from_cloud_provider(cloud_provider: str) -> str:
    if cloud_provider.upper() == "AWS":
        password_data: str = AWSSecretAdaptor().get_secret(config.DB_PASSWORD_SECRET_NAME)
        password: str = json.loads(password_data)["password"]
        # url encode password to escape special characters
        password = quote(password)
        # Escape % in the db_url
        password = password.replace('%', '%%')
        return config.DB_URL.format(password=password)
    else:
        raise NotImplementedError(f"No get db_url logic implemented for Cloud provider {cloud_provider}")


def get_db_url():
    # Running on the cloud
    if config.DB_PASSWORD_SECRET_NAME:
        logger.info("Getting DB URL from cloud provider")
        db_url: str = get_db_url_from_cloud_provider(config.CLOUD_PROVIDER)
        print(f"DB URL: '{db_url}'")
        return db_url
    # Running locally
    else:
        logger.info("Using DB URL directly as running locally")
        return config.DB_URL
