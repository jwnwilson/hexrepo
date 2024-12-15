import json
import logging
import os

from monorepo_cloud.secrets.aws import AWSSecretAdaptor

from ..config import config

logger = logging.getLogger(__name__)


# def get_sql_db_url_from_cloud_provider(cloud_provider: str) -> str:
#     if cloud_provider.upper() == "AWS":
#         password_data: str = AWSSecretAdaptor().get_secret(
#             config.DB_PASSWORD_SECRET_NAME
#         )
#         password: str = json.loads(password_data)["password"]
#         # url encode password to escape special characters
#         password = quote(password)
#         return config.DB_URL.format(password=password)
#     else:
#         raise NotImplementedError(
#             f"No get db_url logic implemented for Cloud provider {cloud_provider}"
#         )


def get_sql_db_url() -> str:
    # Running on the cloud
    if os.environ.get("DB_URL_SECRET_NAME"):
        logger.info("Getting DB URL from cloud provider")
        db_url: str = AWSSecretAdaptor.get_secret("DB_URL_SECRET_NAME", default=os.environ.get("DB_URL"))
        return db_url
    # Running locally
    else:
        logger.info("Using DB URL env var directly as running locally")
        return os.environ.get("DB_URL")
