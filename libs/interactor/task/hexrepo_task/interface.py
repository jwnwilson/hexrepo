from abc import ABC
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from hexrepo_db.interface import UOW, Repository
from pydantic import BaseModel


class TaskDTO(BaseModel):
    id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    name: str
    params: Optional[Dict] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    status: str = "pending"
    error: Optional[str] = None


class TaskUpdateDTO(BaseModel):
    params: Optional[Dict] = None
    status: Optional[str] = None
    error: Optional[str] = None
    task_id: Optional[UUID] = None


class TaskCreateDTO(BaseModel):
    name: str
    params: Optional[Dict] = None


# class TaskEvent(BaseModel):
#     id: Optional[UUID] = None
#     task_id: Optional[UUID] = None
#     task_name: str
#     params: Optional[Dict] = None


class TaskArgs(BaseModel):
    task_name: str
    params: Dict


class QueueConfig(BaseModel):
    default_queue: str
    endpoint_url: Optional[str] = None
    queue_url: Optional[str] = None


class QueueAdaptor(ABC):
    def __init__(
        self,
        config: QueueConfig,
    ):
        raise NotImplementedError

    def add_task(self, task_event: TaskDTO, queue_name: Optional[str] = None) -> TaskDTO:
        raise NotImplementedError

    @contextmanager
    def get_task(self) -> Generator[TaskDTO | None, None, None]:
        raise NotImplementedError

    def create_queue(self, queue_name: str):
        raise NotImplementedError

    def delete_queue(self, queue_name: str):
        raise NotImplementedError

    def purge_queue(self, queue_name: str):
        raise NotImplementedError
    
    def get_queue_url(self, queue_name: Optional[str] = None) -> str:
        raise NotImplementedError


class TaskUOW(UOW):
    @property
    def task(self) -> Repository:
        raise NotImplementedError
