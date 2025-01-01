import logging
from datetime import datetime
from functools import reduce
from operator import and_
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from ...exception import RecordNotFound
from ...interface import (
    ModelDTO,
    ModelDTOType,
    PaginatedData,
    Repository,
    UpdateModelDTO,
)

logger = logging.getLogger(__name__)

QueryParams = Dict[str, Any]
FilterParam = Dict[str, Any]


class DynamoRepository(Repository):
    model_dto: ModelDTOType = BaseModel

    def __init__(
        self,
        dyn_resource: DynamoDBServiceResource,
        table: str,
        required_filters: Optional[FilterParam] = None,
    ):
        self.dyn_resource: DynamoDBServiceResource = dyn_resource
        self.default_filters: Optional[FilterParam] = required_filters
        self.table_name: str = table
        self._table: Optional[Table] = None

    @property
    def table(self) -> Table:
        """
        Determines whether a table exists. As a side effect, stores the table in
        a member variable.

        :param table_name: The name of the table to check.
        :return: True when the table exists; otherwise, False.
        """
        if self._table:
            return self._table
        try:
            table = self.dyn_resource.Table(self.table_name)
            table.load()
            self._table = table
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                logger.error(f"Table not found: {self.table_name}")
                raise
            else:
                logger.error(f"Error accessing table: {self.table_name}. Error: {err}")
                raise

        return self._table

    @table.setter
    def table(self, table: Optional[Table]) -> None:
        self._table = table

    def table_exists(self) -> bool:
        try:
            if self.table:
                return True
        except ClientError:
            pass
        return False

    def _build_query_params(
        self,
        filters: Optional[FilterParam] = None,
    ) -> Dict[str, Any]:
        combined_filters: FilterParam = self.default_filters or {}
        if filters:
            combined_filters.update(**filters)
        if combined_filters:
            return {"FilterExpression": self._add_expressions(filters)}
        else:
            return {}

    def _list_to_dto(self, items: List[Dict[str, Any]]) -> List[ModelDTO]:
        return [self.model_dto(**item) for item in items]

    def _add_expressions(self, filters: Dict[str, Any]) -> List[Any]:
        if filters:
            conditions: List[Any] = []
            for key, value in filters.items():
                if isinstance(value, (UUID, datetime)):
                    value = str(value)
                if isinstance(value, str):
                    conditions.append(Attr(key).eq(value))
                elif isinstance(value, list):
                    value = [
                        str(v) if isinstance(v, (UUID, datetime)) else v for v in value
                    ]
                    key = key.split("__")[0]
                    conditions.append(Attr(key).is_in([v for v in value]))
            return reduce(and_, conditions)

    def _convert_fields_to_str(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        for key in record_data.keys():
            if isinstance(record_data[key], (UUID, datetime)):
                record_data[key] = str(record_data[key])
        return record_data
    
    def create(self, obj_in: ModelDTO) -> ModelDTO:
        record_data: Dict[str, Any] = obj_in.model_dump()
        record_data["id"] = str(uuid4())
        # Handle datetime and uuid fields
        record_data = self._convert_fields_to_str(record_data)
        self.table.put_item(Item=record_data)
        return self.model_dto(**record_data)

    def read(self, id: UUID) -> ModelDTO:
        try:
            table_data: Dict[str, Any] = self.table.get_item(Key={"id": str(id)})[
                "Item"
            ]
            return self.model_dto(**table_data)
        except KeyError:
            raise RecordNotFound(f"Record not found: {id} in table: {self.table_name}")

    def read_multi(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page_size: int = 100,
        page_number: int = 1,
        order_by: str = "-created_at",
    ) -> PaginatedData[ModelDTO]:
        query_params: QueryParams = self._build_query_params(filters)
        if page_size < 0:
            query_params["Limit"] = page_size
        table_data: Dict[str, Any] = self.table.scan(**query_params)
        results: List[ModelDTO] = self._list_to_dto(table_data["Items"])
        return PaginatedData(
            results=results,
            total=len(results),
            page_size=page_size,
            page_number=page_number,
        )

    def update(
        self, id: UUID, obj_in: UpdateModelDTO, merge_objects: bool = False
    ) -> ModelDTO:
        update_expression = "SET "
        expression_attr_values = {}
        expression_attr_names = {}
        update_expressions = []

        existing_obj: BaseModel = self.read(id)
        update_obj: Dict[str, Any] = existing_obj.model_dump()
        update_obj.update(**obj_in.model_dump(exclude_unset=True))
        del update_obj["id"]

        for key in update_obj.keys():
            expression_value: Any = (
                str(update_obj[key])
                if isinstance(update_obj[key], (UUID, datetime))
                else update_obj[key]
            )
            update_expressions.append(f"#{key} = :{key}")
            expression_attr_values[f":{key}"] = expression_value
            expression_attr_names[f"#{key}"] = key

        update_expression += ", ".join(update_expressions)

        try:
            self.table.update_item(
                Key={"id": str(id)},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attr_values,
                ExpressionAttributeNames=expression_attr_names,
            )
        except ClientError as err:
            logger.error(
                f"Couldn't update record {id} in table {self.table_name}:Error: {err} ",
                id,
                self.table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

        return self.read(id)

    def delete(self, id: UUID) -> None:
        try:
            self.read(id)
            self.table.delete_item(Key={"id": str(id)})
            print("here")
        except ClientError as err:
            msg: str = f"Couldn't delete record {id}. Error: {err}"
            logger.error(msg)
            raise

    def _generate_attribute_definitions(self) -> List[Dict[str, Any]]:
        attribute_definitions: List[Dict[str, Any]] = []
        field: str

        for field in self.model_dto.model_fields:
            field_type: FieldInfo = self.model_dto.model_fields[field]
            if field_type.annotation in (UUID, str, datetime):
                attribute_definitions.append(
                    {"AttributeName": field, "AttributeType": "S"}
                )
            if field_type.annotation in (int, float):
                attribute_definitions.append(
                    {"AttributeName": field, "AttributeType": "N"}
                )
        return attribute_definitions

    def create_table(self) -> None:
        if self.table_exists():
            logger.info(f"Skipping Table {self.table_name} create as it does not exist")
            return
        try:
            # attr_defs: List[Dict[str, Any]] = []
            # attr_defs += self._generate_attribute_definitions()
            self.table = self.dyn_resource.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {"AttributeName": "id", "KeyType": "HASH"},  # Partition key
                    # {"AttributeName": "company_id", "KeyType": "HASH"},  # Partition key
                    # {"AttributeName": "id", "KeyType": "HASH"},  # Sort key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "id", "AttributeType": "S"},  # Partition key
                    # {"AttributeName": "company_id", "AttributeType": "S"},  # Sort key
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 10,
                    "WriteCapacityUnits": 10,
                },
            )
            self.table.wait_until_exists()
            logger.info(f"Table {self.table_name} created successfully")
        except ClientError as err:
            logger.error(f"Couldn't create table {self.table_name}. Error: {err}")
            raise

    def delete_table(self):
        """
        Deletes the table.
        """
        if not self.table_exists():
            logger.info(f"Skipping Table {self.table_name} delete as it does not exist")
            return
        try:
            self.table.delete()
            self.table = None
            logger.info(f"Table {self.table_name} deleted successfully")
        except ClientError as err:
            logger.error(f"Couldn't delete table {self.table_name}. Error: {err}")
            raise
