import logging
import os
from functools import wraps
from typing import Dict

import boto3

from .interface import SecretAdaptor

logger = logging.getLogger(__name__)


def aws_secret_cache(func):
    # In aws lambda we can cache data across requests for multiple calls in /tmp
    # This is the cheapest way to cache data in AWS Lambda
    @wraps(func)
    def wrapper(*args, **kwargs):
        # hash the function name and the arguments to create a unique key
        key = f"{func.__name__}-{hash(args)}- {hash(kwargs)}"
        if key in set(os.listdir("/tmp")):
            with open(f"/tmp/{key}", "r") as f:
                return f.read()
        result = func(*args, **kwargs)
        with open(f"/tmp/{key}", "w") as f:
            f.write(result)
        return result

    return wrapper


class AWSSecretAdaptor(SecretAdaptor):
    def __init__(self) -> None:
        self.client = boto3.client("secretsmanager")

    @aws_secret_cache
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
