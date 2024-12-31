from abc import ABC
from uuid import UUID
from pydantic import BaseModel

from .app import TaskEvent


class TaskArgs(BaseModel):
    task_name: str
    params: dict


class TaskData(BaseModel):
    task_id: UUID
    task_name: str
    params: dict
    status: str


class QueueConfig(BaseModel):
    queue: str


class QueueAdapter(ABC):
    def __init__(self, config: QueueConfig,):
        raise NotImplementedError

    def add_task(self, task_event: TaskEvent) -> TaskData:
        raise NotImplementedError

    def get_task(self, task_id: UUID) -> TaskData:
        raise NotImplementedError
