import logging
from typing import Dict
from celery import Celery

from ...config import TaskConfig

logger = logging.getLogger(__name__)


def celery_app(config: TaskConfig) -> Celery:
    if config.cloud_provider == "aws":
        aws_access_key = config.aws_access_key
        aws_secret_key = config.aws_secret_key

        # Broker settings
        queue_map = {
            key: {
                "url": value,
                "access_key_id": aws_access_key,
                "secret_access_key": aws_secret_key,
            } for key, value in config.queues.items()
        }
        queue_url: str = f"sqs://{aws_access_key}:{aws_secret_key}@"
        broker_options: Dict = {
            "region": config.region,
            "predefined_queues": queue_map,
        }
        if config.queue_endpoint:
            broker_options["endpoint_url"] = config.queue_endpoint
            queue_url = config.queue_endpoint.replace("http://", "sqs://")

        # Results backend settings
        backend_table: str = config.backend_table
        if config.backend_endpoint:
            result_backend: str = f'dynamodb://@{config.backend_endpoint}/{backend_table}'
        else:
            result_backend: str = f'dynamodb://{aws_access_key}:{aws_secret_key}@{config.region}/{backend_table}'

        app: Celery = Celery(
            "app",
            broker_url=queue_url,
            broker_connection_retry_on_startup=True,
            broker_connection_retry=True,
            broker_transport_options=broker_options,
            task_create_missing_queues=False,
            backend=result_backend,
            task_default_queue=config.default_queue
        )
    
    return app
