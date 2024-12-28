import logging
import os
from typing import Any, List, Optional

import boto3
from mypy_boto3_s3.client import S3Client

from ..config import AWSConfig
from .exceptions import StorageAlreadyExists, StorageInvalid
from .interface import StorageAdaptor, StorageConfig, StorageData, UploadUrlData

logger = logging.getLogger(__name__)


class S3Adaptor(StorageAdaptor):
    def __init__(self, storage_config: StorageConfig) -> None:
        self.bucket_name = storage_config.aws_bucket
        self.s3 = boto3.resource("s3")
        self.client: S3Client = boto3.client("s3")
        self.bucket = self.s3.Bucket(self.bucket_name)
        self.public_url_timeout: Optional[int] = storage_config.public_url_timeout
        self._upload_client: Optional[S3Client] = None

        self.url_prefix: str = (
            f"https://{self.bucket_name}.s3-{storage_config.aws_region}.amazonaws.com/"
        )

    @property
    def upload_client(self) -> Any:
        if self._upload_client:
            return self._upload_client

        s3_client = boto3.client("s3")
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

    @classmethod
    def create_bucket(cls, bucket_name: str, config: AWSConfig) -> None:
        client = boto3.client("s3")
        try:
            # Create S3 bucket
            client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": config.AWS_REGION},  # type: ignore
            )
        except Exception as err:
            if "BucketAlreadyOwnedByYou" in str(err):
                raise StorageAlreadyExists(
                    f"Bucket {bucket_name} already exists, skipping..."
                )
            elif "The specified bucket is not valid." in str(err):
                raise StorageInvalid(
                    "The bucket name can be between 3 and 63 characters long, and can contain only lower-case characters, numbers, periods, and dashes."
                )
