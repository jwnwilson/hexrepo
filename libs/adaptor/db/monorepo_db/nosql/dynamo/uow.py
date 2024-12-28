import contextlib
from typing import Any, Dict, Generator, Optional

import boto3
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource

from ...interface import UOW


class BaseDynamoUOW(UOW):
    def __init__(self, db_url: str, required_filters: Optional[Dict[str, str]] = None):
        self._db_url: str = db_url
        self._required_filters: Optional[Dict[str, str]] = required_filters
        # Auth using env vars
        if db_url:
            self.resource: DynamoDBServiceResource = boto3.resource(
                "dynamodb", endpoint_url=db_url
            )
        else:
            self.resource: DynamoDBServiceResource = boto3.resource("dynamodb")

    @contextlib.contextmanager
    def transaction(self) -> Generator[Any, None, None]:
        raise NotImplementedError(
            "Details to implement: https://aws.amazon.com/blogs/aws/new-amazon-dynamodb-transactions/"
        )

    # Used for testing
    def create_all(self) -> None:
        raise NotImplementedError

    def drop_all(self) -> None:
        raise NotImplementedError
