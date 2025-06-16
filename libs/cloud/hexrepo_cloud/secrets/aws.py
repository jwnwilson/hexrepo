import functools
import logging
import os
from typing import Callable, Dict, Optional

import boto3

from .interface import SecretAdaptor

logger = logging.getLogger(__name__)

RUNNING_ON_AWS = os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None


def secret_cache(func: Callable) -> Callable:
    # Check if the secret is cached in /tmp as fetching secrets can be slow
    # This is the cheapest and quickest method for caching in aws lambdas
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Optional[str]:
        secret_name: str = args[1]
        if RUNNING_ON_AWS and secret_name in set(os.listdir("/tmp")):
            logger.info(f"Secret: {secret_name} retrieved from file cache.")
            with open(f"/tmp/{secret_name}", "r") as f:
                return f.read()
        secret_value: str = func(*args, **kwargs)
        if RUNNING_ON_AWS and secret_value:
            with open(f"/tmp/{secret_name}", "w") as f:
                f.write(secret_value)
        return secret_value

    return wrapper


class AWSSecretAdaptor(SecretAdaptor):
    def __init__(self) -> None:
        self.client = boto3.client("secretsmanager")

    @secret_cache
    def get_secret(self, secret_name: str) -> str:
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
