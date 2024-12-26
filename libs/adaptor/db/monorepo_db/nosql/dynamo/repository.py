import logging
from functools import reduce
from operator import and_
from typing import Any, Dict, List, Optional
from uuid import UUID

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table
from pydantic import BaseModel

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
        self, dyn_resource: DynamoDBServiceResource, table: str, required_filters: Optional[FilterParam] = None,
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
                logger.error(
                    f"Error accessing table: {self.table_name}. Error: {err}"
                )
                raise
                
        return self._table
    
    def table_exists(self) -> bool:
        try:
            if self.table:
                return True
        except ClientError:
            pass
        return False

    def _apply_default_filters(self, query_params: QueryParams) -> QueryParams:
        if self.default_filters:
            query_params["FilterExpression"] += self._add_expressions(self.default_filters)
        return query_params

    def _build_query_params(self, filters: Optional[FilterParam] = None, query_params: Optional[QueryParams] = None) -> Dict[str, Any]:
        query_params: QueryParams = query_params or {"FilterExpression": []}
        if filters:
            query_params["FilterExpression"] += self._add_expressions(filters)
        query_params = self._apply_default_filters(query_params)

        return query_params
    
    def _list_to_dto(self, items: List[Dict[str, Any]]) -> List[ModelDTO]:
        return [self.model_dto(**item.__dict__) for item in items]

    def _add_expressions(self, filters: Dict[str, Any]) -> List[Any]:
        if filters:
            conditions: List[Any] = []
            for key, value in filters.items():
                if isinstance(value, str):
                    conditions.append(Attr(key).eq(value))
                if isinstance(value, list):
                    conditions.append(Attr(key).is_in([v for v in value]))
            return reduce(and_, conditions)

    def create(self, obj_in: ModelDTO) -> ModelDTO:
        record_data: Dict[str, Any] = obj_in.model_dump()
        record_data["id"] = str(UUID())
        table_data: Dict[str, Any] = self.table.put_item(Item=record_data)
        return self.model_dto(**table_data)
    
    def read(self, record_id: UUID) -> ModelDTO:
        try:
            table_data: dict = self.table.get_item(
                Key={
                    "id": record_id
                }
            )["Item"]
            return self.model_dto(**table_data)
        except KeyError:
            raise RecordNotFound("Record not found: {record_id} in table: {table}")

    def read_multi(
            self, 
            filters: Optional[Dict[str, Any]] = None,
            page_size: int = 100,
            page_number: int = 1,
            order_by: str = "-created_at"
        ) -> PaginatedData[ModelDTO]:
        
        table_data: List[dict] = self.table.scan(
            **self._build_query_params(filters), Limit=page_size
        )
        results: List[ModelDTO] = self._list_to_dto(table_data)
        return PaginatedData(
            results=results, total=len(results), page_size=page_size, page_number=page_number
        )

    def update(self, record_id: UUID, obj_in: UpdateModelDTO, merge_objects: bool = False) -> ModelDTO:
        update_expression = "SET "
        expression_attr_values = {}
        expression_attr_names = {}
        update_expressions = []

        for key in obj_in.model_dump().keys():
            update_expressions.append(f"#{key} = :{key}")
            expression_attr_values[f":{key}"] = getattr(obj_in, key)
            expression_attr_names[f"#{key}"] = key

        update_expression += ", ".join(update_expressions)

        try:
            table_data: Dict[str, Any] = self.table.update_item(
                Key={"id": record_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attr_values,
                ExpressionAttributeNames=expression_attr_names,
            )
        except ClientError as err:
            logger.error(
                f"Couldn't update record {record_id} in table {self.table_name}:Error: {err} ",
                record_id,
                self.table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        return self.model_dto(**table_data.__dict__)

    def delete(self, id: UUID) -> None:
        try:
            self.table.delete_item(Key={"id": id})
        except ClientError as err:
            logger.error(
                f"Couldn't delete record {id}. Error: {err}"
            )
            raise

    def _generate_attribute_definitions(self) -> List[Dict[str, Any]]:
        attribute_definitions = []

        for field in self.model_dto.model_fields():
            if field.type_ == str:
                attribute_definitions.append(
                    {"AttributeName": field.name, "AttributeType": "S"}
                )
            if field.type_ == int:
                attribute_definitions.append(
                    {"AttributeName": field.name, "AttributeType": "N"}
                )
        return attribute_definitions


    def create_table(self) -> None:
        if self.table_exists():
            return
        try:
            attr_defs: List[Dict[str, Any]] = self._generate_attribute_definitions()
            self.table = self.dyn_resource.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {"AttributeName": "id", "KeyType": "HASH"},  # Partition key
                    # {"AttributeName": "company_id", "KeyType": "RANGE"},  # Sort key
                ],
                AttributeDefinitions=attr_defs,
                # ProvisionedThroughput={
                #     "ReadCapacityUnits": 10,
                #     "WriteCapacityUnits": 10,
                # },
            )
            self.table.wait_until_exists()
        except ClientError as err:
            logger.error(
                f"Couldn't create table {self.table_name}. Error: {err}"
            )
            raise

        # Wait until the table exists.
        self.table.wait_until_exists() 
    
    def delete_table(self):
        """
        Deletes the table.
        """
        if not self.table_exists():
            return
        try:
            self.table.delete()
            self.table = None
        except ClientError as err:
            logger.error(
                f"Couldn't delete table {self.table_name}. Error: {err}"
            )
            raise
