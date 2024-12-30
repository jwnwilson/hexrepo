import json
import logging
import uuid

import boto3

from hex_lib.ports.task import TaskAdapter, TaskArgs, TaskData
from hex_lib.ports.user import UserData

logger = logging.getLogger(__name__)


class SqsTaskAdapter(TaskAdapter):
    def __init__(self, config, user: UserData):
        # Create SQS client
        self.sqs = boto3.client("sqs")
        self.queue_url = config["queue"]
        self.user = user

    def create_task(self, task_args: TaskArgs) -> TaskData:
        # Send message to SQS queue
        task_data = TaskData(
            task_id=str(uuid.uuid4()),
            user_id=self.user.user_id,
            task_name=task_args.task_name,
            params=task_args.params,
            status="Pending",
        )

        logger.info(f"Creating task: {task_data.task_id}")
        sqs_resp = self.sqs.send_message(
            QueueUrl=self.queue_url, MessageBody=(json.dumps(task_data.dict()))
        )
        sqs_id = sqs_resp["MessageId"]
        logger.info(f"Created task: {task_data.task_id} SQS event with id: {sqs_id}")

        return task_data

    def get_task(self) -> TaskData:
        # Get a message from sqs queue
        sqs_resp = self.sqs.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=1,
            MessageAttributeNames=["All"],
            VisibilityTimeout=0,
            WaitTimeSeconds=0,
        )

        return TaskData(
            task_id=sqs_resp["MessageId"], status="processing", data=sqs_resp
        )
