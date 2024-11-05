import uuid
from abc import ABC
from typing import List, Optional

from pydantic import BaseModel


class StorageData(BaseModel):
    path: str


class UploadUrlData(BaseModel):
    upload_url: str
    fields: dict


class StorageConfig(BaseModel):
    pass


class StorageAdapter(ABC):
    def __init__(self, config: StorageConfig) -> None:
        pass

    def create_folder(self, path: str):
        raise NotImplementedError

    def list(self, path: str) -> List[str]:
        raise NotImplementedError

    def upload_url(self, path: str) -> UploadUrlData:
        raise NotImplementedError

    def save(self, source_file_path: str, target_file_path: str) -> StorageData:
        raise NotImplementedError

    def load(self, source_file_path: str, target_file_path: str) -> StorageData:
        raise NotImplementedError