import logging
import os
from typing import Any, List, Optional

import boto3  # type: ignore

from .config import config
from .interface import StorageAdaptor, StorageConfig, StorageData, UploadUrlData

logger = logging.getLogger(__name__)


class S3Adaptor(StorageAdaptor):
    def __init__(self, storage_config: StorageConfig) -> None:
        self.bucket_name = storage_config.aws_bucket
        self.s3 = boto3.resource("s3")
        self.client = boto3.client("s3")
        self.bucket = self.s3.Bucket(self.bucket_name)
        self.user = storage_config.aws_auth.get("user")
        self.upload_prefix = storage_config.aws_upload_prefix
        self.upload_user_access_id = storage_config.aws_auth.get(
            "upload_user_access_id"
        )
        self.upload_user_secret_key = storage_config.aws_auth.get(
            "upload_user_secret_key"
        )
        self.public_url_timeout = config.public_url_timeout
        self._upload_client = None

        if not self.user:
            raise RuntimeError("Auth user is not set")
        if not self.upload_prefix:
            raise RuntimeError("Upload prefix is not set")
        if not self.upload_user_access_id:
            raise RuntimeError("Upload access id is not set")
        if not self.upload_user_secret_key:
            raise RuntimeError("Upload secret key is not set")

        self.url_prefix = (
            f"https://{self.bucket_name}.s3-{config.aws_default_region}.amazonaws.com/"
        )

    @property
    def upload_client(self) -> Any:
        if self._upload_client:
            return self._upload_client

        client = boto3.client("ssm")
        access_id = client.get_parameter(
            Name=self.upload_user_access_id, WithDecryption=True
        )
        secret_key = client.get_parameter(
            Name=self.upload_user_secret_key, WithDecryption=True
        )
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=access_id["Parameter"]["Value"],
            aws_secret_access_key=secret_key["Parameter"]["Value"],
        )
        self._upload_client = s3_client

        return s3_client

    def _get_url(self, key: str) -> str:
        return self.url_prefix + key

    def _get_key(self, url: str) -> str:
        key = url.replace(self.url_prefix, "")
        return key

    def get_public_url(self, storage_path: str) -> str:
        public_url: str = self.upload_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": storage_path},
            ExpiresIn=self.public_url_timeout,
        )
        return public_url

    def create_folder(self, path: str) -> None:
        if not path.endswith("/"):
            path = path + "/"
        self.client.put_object(Bucket=self.bucket_name, Key=path)

    def upload_url(self, path: str) -> UploadUrlData:
        upload_data = self.upload_client.generate_presigned_post(
            Bucket=self.bucket_name, Key=path, ExpiresIn=self.public_url_timeout
        )
        return UploadUrlData(
            upload_url=upload_data["url"], fields=upload_data["fields"]
        )

    def list(
        self,
        path: str,
        include_files: Optional[bool] = True,
        include_folders: Optional[bool] = True,
        as_urls: Optional[bool] = False,
    ) -> List[str]:
        prefix: str = path
        objs = self.client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        results: List[str] = []
        if include_files:
            results = results + [obj["Key"] for obj in objs.get("Contents", [])]
        if include_folders:
            results = results + [
                obj["Prefix"] for obj in objs.get("CommonPrefixes", [])
            ]
        if as_urls:
            results = [self._get_url(r) for r in results]
        return sorted(results)

    def save(self, source_path: str, target_path: str) -> StorageData:
        logger.info(
            f"Saving file: {source_path} to s3 bucket: {self.bucket_name}, key: {target_path}"
        )
        self.bucket.upload_file(source_path, target_path)
        return StorageData(path=self._get_url(target_path))

    def load(self, source_path: str, target_path: str) -> StorageData:
        logger.info(
            f"Loading file: {source_path} from s3 bucket: {self.bucket_name}, to path: {target_path}"
        )
        target_dir = "/".join(target_path.split("/")[:-1])
        os.makedirs(target_dir, exist_ok=True)
        self.client.download_file(self.bucket_name, source_path, target_path)
        return StorageData(path=target_path)

    def delete(self, path: str) -> None:
        self.client.delete_object(Bucket=self.bucket_name, Key=path)
        logger.info(f"Deleted file: {path} from s3 bucket: {self.bucket_name}")
