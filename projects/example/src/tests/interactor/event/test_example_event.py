from hexrepo_task.interactor.event.app import TaskApp, TaskPromise
from hexrepo_task.interface import QueueAdaptor

from app.adaptor.db.sql import SqlUOW
from app.interactor.event.tasks.app import create_example_task
from app.domain.example import CreateExampleDTO


def test_example_event_create_example_task(
    task_app: TaskApp, queue: QueueAdaptor, uow: SqlUOW
):
    task_promise: TaskPromise = create_example_task.queue_task(
        example=CreateExampleDTO(name="example", url="https://example.com", location="example location")
    )
    assert uow.example.read_multi().total == 0

    with queue.get_task() as task_event:
        assert task_event is not None
        aws_event = {
            "Records": [
                {
                    "messageId": "ea0d3a3c-3530-46a1-85c3-eb50048e38f1",
                    "receiptHandle": "AQEBy0pdJ2vI9eHBeVeDu4xMumt1XB/AW59ES0vYLy8XsiajR22asg6wkQO0GzQOtrBv4whyFjnJYu20PaaiFYGPoImM61YC2hFeaIcCFynqt9WtRlANHVz81S5BFJa7UH1PGTTmBYVIN4Y+gQbzo5X2LxpxH+HHryMREBelqDyop1cNlVVtTvvWY8TE9p/uAgSsYsQooWR/jomLyBAUCuHXkAhG4rkPukqZo/kAF9HqW2Itkk3hIecjrV+c/FIFuLfQkMeJoFBFP9sDgWnXrTzZTt0mdbxh3OnauYwJfI2Bwj2sebf3bdnWysf7erpXLdDZj9RzctKSq7aEXae4VbqWRgRAdSGaGwSYU8F5OqeVP48nXrGnptAPBmtkAPyfqLLW46U8/6unClZetulKf348Hw==",
                    "body": task_event.model_dump_json(),
                    "attributes": {
                        "ApproximateReceiveCount": "1",
                        "AWSTraceHeader": "Root=1-677c608c-124564841d27101c30d47485;Parent=83f20d58e10d5343;Sampled=1;Lineage=1:46486e53:0",
                        "SentTimestamp": "1736204431263",
                        "SenderId": "AROAZ2RIRVGEAUG7KZE3F:example_api_default",
                        "ApproximateFirstReceiveTimestamp": "1736204431270",
                    },
                    "messageAttributes": {},
                    "md5OfBody": "2f4251ba16f3d9f9d64b06ad16de9013",
                    "eventSource": "aws:sqs",
                    "eventSourceARN": "arn:aws:sqs:eu-west-1:675468650888:example_default_tasks",
                    "awsRegion": "eu-west-1",
                }
            ]
        }
        task_app.handle(aws_event)

    task_promise.wait()
    assert uow.example.read_multi().total == 1
    assert task_promise.task.status == "completed"
