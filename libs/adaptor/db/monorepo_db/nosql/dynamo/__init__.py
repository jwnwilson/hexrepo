from enum import Enum
from functools import reduce
from operator import and_
from typing import Any, Dict, List

import boto3
from boto3.dynamodb.conditions import Attr
from pydantic import BaseModel

from hex_lib.ports.db import DbAdapter, ListParams
from hex_lib.ports.user import UserData

from ..exceptions import RecordNotFound


class KeyType(Enum):
    HASH = "HASH"
    RANGE = "RANGE"


class AttributeType(Enum):
    string = "S"
    number = "N"
    binary = "B"


class KeySchema(BaseModel):
    name: str
    type: KeyType


class AttributeDefinitions(BaseModel):
    name: str
    type: AttributeType


class TableDefinition(BaseModel):
    key_schema: List[KeySchema]
    attribute_definitions: List[AttributeDefinitions]


class DynamodbAdapter(DbAdapter):
    def __init__(
        self, config: dict, user: UserData, part_key_name: str, sort_key_name: str
    ):
        # Get the service resource.
        self.client = boto3.resource("dynamodb")
        self.config = config
        self.part_key_name = part_key_name
        self.sort_key_name = sort_key_name
        self.user = user

    def _get_table(self, table):
        return self.client.Table(table)

    def _build_query_params(self, params: ListParams):
        query_params = {}
        filters: Dict[str, Any] = {}
        if params.filters:
            filters = {**filters, **params.filters}
        if filters:
            query_params["FilterExpression"] = self._add_expressions(filters)

        return query_params

    def _add_expressions(self, filters: dict):
        if filters:
            conditions = []
            for key, value in filters.items():
                if isinstance(value, str):
                    conditions.append(Attr(key).eq(value))
                if isinstance(value, list):
                    conditions.append(Attr(key).is_in([v for v in value]))
            return reduce(and_, conditions)

    def read(self, table: str, record_id: str) -> dict:
        try:
            table_data: dict = self._get_table(table).get_item(
                Key={
                    self.part_key_name: self.user.user_id,
                    self.sort_key_name: record_id,
                }
            )["Item"]
            return table_data
        except KeyError:
            raise RecordNotFound("Record not found: {record_id} in table: {table}")

    def list(self, table: str, params: ListParams) -> List[dict]:
        table_data: List[dict] = self._get_table(table).scan(
            **self._build_query_params(params), Limit=params.limit
        )
        return table_data

    def create(self, table: str, record_data: dict) -> dict:
        record_data[self.part_key_name] = self.user.user_id
        table_data: dict = self._get_table(table).put_item(Item=record_data)
        return table_data

    def update(self, table: str, record_id: str, record_data: dict) -> dict:
        update_expression = "SET "
        expression_attr_values = {}
        expression_attr_names = {}
        update_expressions = []

        for key in record_data.keys():
            update_expressions.append(f"#{key} = :{key}")
            expression_attr_values[f":{key}"] = record_data[key]
            expression_attr_names[f"#{key}"] = key

        update_expression += ", ".join(update_expressions)

        table_data: dict = self._get_table(table).update_item(
            Key={self.part_key_name: self.user.user_id, self.sort_key_name: record_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attr_values,
            ExpressionAttributeNames=expression_attr_names,
        )
        return table_data

    def create_table(self, table: str, **kwargs):
        table_definition: TableDefinition = kwargs.pop("table_definition")
        key_schema = [
            {"AttributeName": key.name, "KeyType": key.type.value}
            for key in table_definition.key_schema
        ]
        attribute_definitions = [
            {"AttributeName": attr.name, "AttributeType": attr.type.value}
            for attr in table_definition.attribute_definitions
        ]
        if "BillingMode" not in kwargs:
            kwargs["BillingMode"] = "PAY_PER_REQUEST"

        table = self.client.create_table(
            TableName=table,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            **kwargs,
        )

        # Wait until the table exists.
        table.wait_until_exists()  # type: ignore

        return table
