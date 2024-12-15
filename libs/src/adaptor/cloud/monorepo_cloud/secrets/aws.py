import logging
from typing import Dict

import boto3  # type: ignore

from .interface import SecretAdaptor

logger = logging.getLogger(__name__)


class AWSSecretAdaptor(SecretAdaptor):
    client = None   

    @classmethod
    def client(cls):
        if not cls.client:
            cls.client = boto3.client("secretsmanager")
        
        return cls.client


    @classmethod
    def get_secret(cls, secret_name: str) -> str:
        logger.info(f"Getting secret: {secret_name}")
        try:
            get_secret_value_response: Dict[str, str] = cls.client.get_secret_value(
                SecretId=secret_name
            )
            logger.info(f"Secret: {secret_name} retrieved successfully.")
            return get_secret_value_response["SecretString"]
        except Exception as e:
            msg = f"The requested secret {secret_name} was not found."
            logger.exception(msg)
            raise
