import logging
import os
from typing import Dict, Optional

import boto3

from .interface import SecretAdaptor

logger = logging.getLogger(__name__)


def aws_cache(secret_name: str) -> Optional[str]:
    # Check if the secret is already cached in /tmp this is the cheapest and quickest method
    # for caching in aws lambdas
    if secret_name in set(os.listdir("/tmp")):
        with open(f"/tmp/{secret_name}", "r") as f:
            return f.read()
    else:
        return None  


class AWSSecretAdaptor(SecretAdaptor):
    def __init__(self) -> None:
        self.client = boto3.client("secretsmanager")

    def get_secret(self, secret_name: str) -> str:
        secret_value: str = aws_cache(secret_name)
        if secret_value:
            logger.info(f"Secret: {secret_name} retrieved from file cache.")
            return secret_value
        logger.info(f"Getting secret: {secret_name}")
        try:
            get_secret_value_response: Dict[str, str] = self.client.get_secret_value(
                SecretId=secret_name
            )
            logger.info(f"Secret: {secret_name} retrieved successfully.")
            return get_secret_value_response["SecretString"]
        except Exception:
            msg = f"The requested secret {secret_name} was not found."
            logger.exception(msg)
            raise
        
