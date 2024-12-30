from abc import ABC
from uuid import UUID

from libs.interactor.task.hexrepo_task.app import TaskEvent
from pydantic import BaseModel


class TaskArgs(BaseModel):
    task_name: str
    params: dict


class TaskData(BaseModel):
    task_id: UUID
    task_name: str
    params: dict
    status: str


class TaskConfig(BaseModel):
    queue: str


class TaskAdapter(ABC):
    def __init__(self, config: TaskConfig):
        raise NotImplementedError

    def queue(self, task_event: TaskEvent) -> TaskData:
        raise NotImplementedError

    def get_task(self, task_id: UUID) -> TaskData:
        raise NotImplementedError
