from abc import ABC
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class StorageData(BaseModel):
    path: str


class UploadUrlData(BaseModel):
    upload_url: str
    fields: Dict[str, Any]


class StorageConfig(BaseModel):
    aws_bucket: str
    aws_region: str
    public_url_timeout: Optional[int] = None


class StorageAdaptor(ABC):
    def __init__(self, config: StorageConfig) -> None:
        pass

    def create_folder(self, path: str) -> None:
        raise NotImplementedError

    def list(self, path: str) -> List[str]:
        raise NotImplementedError

    def upload_url(self, path: str) -> UploadUrlData:
        raise NotImplementedError

    def save(self, source_file_path: str, target_file_path: str) -> StorageData:
        raise NotImplementedError

    def load(self, source_file_path: str, target_file_path: str) -> StorageData:
        raise NotImplementedError
    
    def read(self, path: str) -> str:
        raise NotImplementedError
    
    def write(self, path: str, data: str) -> None:
        raise NotImplementedError

    def delete(self, path: str) -> None:
        raise NotImplementedError
