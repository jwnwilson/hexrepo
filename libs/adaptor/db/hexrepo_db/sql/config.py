import logging
from urllib.parse import quote

from hexrepo_cloud.secrets.aws import AWSSecretAdaptor

from ..config import config

logger = logging.getLogger(__name__)


def get_sql_db_url_from_cloud_provider(cloud_provider: str, read_only: bool = False) -> str:
    if cloud_provider.upper() == "AWS":
        password_data: str = AWSSecretAdaptor().get_secret(
            config.DB_PASSWORD_SECRET_NAME
        )
        password: str = password_data
        # url encode password to escape special characters
        password = quote(password)
        if read_only:
            if not config.DB_RO_URL:
                raise ValueError("DB_RO_URL env var not set")
            return config.DB_RO_URL.format(password=password)
        else:
            return config.DB_URL.format(password=password)
    else:
        raise NotImplementedError(
            f"No get db_url logic implemented for Cloud provider {cloud_provider}"
        )


def get_sql_db_url(read_only: bool = False) -> str:
    # Running on the cloud
    if config.DB_PASSWORD_SECRET_NAME:
        logger.info("Getting DB URL from cloud provider")
        db_url: str = get_sql_db_url_from_cloud_provider(config.CLOUD_PROVIDER, read_only=read_only)
        return db_url
    # Running locally
    else:
        logger.info("Using DB URL env var directly as running locally")
        if read_only:
            if not config.DB_RO_URL:
                raise ValueError("DB_RO_URL env var not set")
            return config.DB_RO_URL
        else:
            return config.DB_URL
    