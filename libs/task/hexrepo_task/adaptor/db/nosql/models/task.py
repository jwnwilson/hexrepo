from hexrepo_db.nosql.dynamo.repository import DynamoRepository

from hexrepo_task.interface import TaskDTO


class TaskRepository(DynamoRepository):
    model_dto = TaskDTO
