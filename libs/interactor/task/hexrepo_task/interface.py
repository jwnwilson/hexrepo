from abc import ABC
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from hexrepo_db.interface import UOW, Repository
from pydantic import BaseModel


class TaskCreateDTO(BaseModel):
    task_id: Optional[UUID] = None
    name: str
    params: Dict[Any]
    created_at: datetime
    updated_at: datetime
    status: str
    error: Optional[Dict[Any]]


class TaskDTO(TaskCreateDTO):
    id: UUID


class TaskUpdateDTO(BaseModel):
    params: Optional[Dict[Any]] = None
    status: Optional[str] = None
    error: Optional[Dict[Any]] = None


# class TaskEvent(BaseModel):
#     id: Optional[UUID] = None
#     task_id: Optional[UUID] = None
#     task_name: str
#     params: Optional[Dict[Any]] = None

class TaskArgs(BaseModel):
    task_name: str
    params: Dict[Any]


class QueueConfig(BaseModel):
    queue: str


class QueueAdapter(ABC):
    def __init__(self, config: QueueConfig,):
        raise NotImplementedError

    def add_task(self, task_event: TaskDTO) -> TaskDTO:
        raise NotImplementedError

    def get_task(self, task_id: UUID) -> TaskDTO:
        raise NotImplementedError


class TaskUOW(UOW):
    @property
    def task(self) -> Repository:
        raise NotImplementedError