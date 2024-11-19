import boto3
import logging
from .interface import SecretAdaptor

logger = logging.getLogger(__name__)


class AWSSecretAdaptor(SecretAdaptor):
    def __init__(self):
        self.client = boto3.client("secretsmanager")

    def get_secret(self, secret_name: str) -> str:
        try:
            get_secret_value_response = self.client.get_secret_value(
                SecretId=secret_name
            )
            logger.info(f"Secret: {secret_name} retrieved successfully.")
            return get_secret_value_response["SecretString"]
        except Exception as e:
            msg = f"The requested secret {secret_name} was not found."
            logger.exception(msg)
            raise
