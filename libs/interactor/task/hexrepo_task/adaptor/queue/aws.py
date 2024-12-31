import json
import logging
import uuid

import boto3

from hexrepo_task.interface import QueueAdapter, TaskArgs, TaskDTO

logger = logging.getLogger(__name__)


class SqsQueueAdapter(QueueAdapter):
    def __init__(self, config, queue_url=None):
        # Create SQS client
        if queue_url:
            self.sqs = boto3.client("sqs", queue_url=queue_url)
        else:
            self.sqs = boto3.client("sqs")
        self.queue_url = config["queue"]

    def add_task(self, task_event: TaskDTO) -> TaskDTO:
        # Send message to SQS queue
        logger.info(f"Creating task: {task_event.id}")
        sqs_resp = self.sqs.send_message(
            QueueUrl=self.queue_url, MessageBody=(json.dumps(task_event.model_dump()))
        )
        sqs_id = sqs_resp["MessageId"]
        task_event.task_id = sqs_id
        logger.info(f"Created task: {task_event.task_id} SQS event with id: {sqs_id}")

        return task_event

    def get_task(self) -> TaskDTO:
        # Get a message from sqs queue
        sqs_resp = self.sqs.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=1,
            MessageAttributeNames=["All"],
            VisibilityTimeout=0,
            WaitTimeSeconds=0,
        )
        return TaskDTO(**json.loads(sqs_resp["Messages"][0]["Body"]))

    def create_queue(self, queue_name: str):
        # Create a new SQS queue
        self.sqs.create_queue(QueueName=queue_name)
        logger.info(f"Created queue: {queue_name}")

    def delete_queue(self, queue_name: str):
        # Delete a SQS queue
        self.sqs.delete_queue(QueueUrl=queue_name)
        logger.info(f"Deleted queue: {queue_name}")
