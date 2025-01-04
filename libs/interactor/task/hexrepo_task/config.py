import logging
import os
from typing import Dict, Optional

from pydantic import BaseModel

logger = logging.getLogger()
# Silence noisy logs from faker
logging.getLogger("faker.factory").setLevel(logging.ERROR)


class TaskConfig(BaseModel):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """
    queues: Dict[str, str] = {"test-queue": "http://localhost.localstack.cloud:4566"}
    default_queue: str = "test-queue"
    backend_table: str = "hexrepo_tasks"
    queue_endpoint: Optional[str] = None
    backend_endpoint: Optional[str] = None

    # Current environment
    project: str = os.environ.get("PROJECT", "hexrepo")
    cloud_provider: str = os.environ.get("CLOUD_PROVIDER", "aws")
    environment: str = os.environ.get("ENVIRONMENT", "dev")
    region: str = os.environ.get("REGION", "eu-west-1")

    # AWS settings
    aws_access_key: str = os.environ.get("AWS_ACCESS_KEY", "")
    aws_secret_key: str = os.environ.get("AWS_SECRET_KEY", "")


config = TaskConfig()  # type: ignore