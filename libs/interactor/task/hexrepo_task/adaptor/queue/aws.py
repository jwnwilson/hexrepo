import json
import logging
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Optional

import boto3

from hexrepo_task.interface import QueueAdaptor, QueueConfig, TaskDTO

logger = logging.getLogger(__name__)


class SqsQueueAdaptor(QueueAdaptor):
    def __init__(self, config: QueueConfig):
        # Create SQS client
        if config.endpoint_url:
            self.sqs = boto3.client("sqs", endpoint_url=config.endpoint_url)
        else:
            self.sqs = boto3.client("sqs")
        self.queue: str = config.queue
        self._queue_url: str = config.queue_url

    @property
    def queue_url(self) -> str:
        if not self._queue_url:
            self._queue_url = self.get_queue_url()
        return self._queue_url

    def _convert_fields_to_str(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        for key in record_data.keys():
            if isinstance(record_data[key], (uuid.UUID, datetime)):
                record_data[key] = str(record_data[key])
        return record_data

    def get_queue_url(self) -> str:
        try:
            return self.sqs.get_queue_url(QueueName=self.queue)["QueueUrl"]
        except self.sqs.exceptions.QueueDoesNotExist:
            raise ValueError(f"Queue does not exist: {self.queue}")
        except Exception as e:
            raise ValueError(f"Error getting queue url: {e}")

    def add_task(self, task_event: TaskDTO) -> TaskDTO:
        # Send message to SQS queue
        logger.info(f"Creating task: {task_event.id}")
        task_data: Dict = self._convert_fields_to_str(task_event.model_dump())
        sqs_resp = self.sqs.send_message(
            QueueUrl=self.queue_url, MessageBody=(json.dumps(task_data))
        )
        task_event.task_id = sqs_resp["MessageId"]
        logger.info(
            f"Created task: {task_event.task_id} SQS event with id: {task_event.task_id}"
        )

        return task_event

    @contextmanager
    def get_task(self) -> Generator[TaskDTO | None, None, None]:
        # Get a message from sqs queue
        sqs_resp: Optional[Dict] = self.sqs.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=1,
            MessageAttributeNames=["All"],
            VisibilityTimeout=0,
            WaitTimeSeconds=0,
        )
        if "Messages" in sqs_resp:
            yield TaskDTO(**json.loads(sqs_resp["Messages"][0]["Body"]))
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=sqs_resp["Messages"][0]["ReceiptHandle"],
            )
        else:
            yield None

    def create_queue(self, queue_name: str):
        # Create a new SQS queue
        self.sqs.create_queue(QueueName=queue_name)
        logger.info(f"Created queue: {queue_name}")

    def delete_queue(self, queue_name: str):
        # Delete a SQS queue
        self.sqs.delete_queue(QueueUrl=self.queue_url)
        logger.info(f"Deleted queue: {queue_name}")

    def purge_queue(self, queue_name: str):
        # Purge a SQS queue
        self.sqs.purge_queue(QueueUrl=self.queue_url)
        logger.info(f"Purged queue: {queue_name}")
