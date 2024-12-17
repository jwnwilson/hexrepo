import os

import pytest

from monorepo_cloud.config import AWSConfig
from monorepo_cloud.storage import S3Adaptor, StorageConfig


@pytest.fixture
def storage_config() -> StorageConfig:
    return StorageConfig(
        aws_bucket="monorepo-jwn",
        aws_upload_prefix="test-upload-prefix",
    )


@pytest.fixture
def aws_config() -> AWSConfig:
    return AWSConfig(
        AWS_ACCOUNT="test-account",
        AWS_REGION="eu-west-1",
        AWS_TF_STATE_BUCKET="test-tf-state-bucket",
    )


@pytest.fixture
def clear_test_data(storage_config: StorageConfig, aws_config: AWSConfig) -> None:
    storage_adaptor: S3Adaptor = S3Adaptor(
        storage_config=storage_config, config=aws_config
    )
    storage_adaptor.delete("test_folder/test_file.txt")
    storage_adaptor.delete("test_folder/")
    try:
        os.remove("tests/test_data/downloaded_test_file.txt")
    except OSError:
        pass


@pytest.mark.e2e
def test_aws_storage_e2e(
    storage_config: StorageConfig, aws_config: AWSConfig, clear_test_data: None
) -> None:
    # Assert credentials are set
    storage_adaptor = S3Adaptor(storage_config, aws_config)

    # Create folder
    aws_folder = "test_folder"
    test_file_name = "test_file.txt"
    storage_adaptor.create_folder(aws_folder)

    # Save file
    test_file_path: str = f"tests/test_data/{test_file_name}"
    with open(test_file_path, "w") as f:
        f.write("test file content")

    storage_adaptor.save(test_file_path, f"{aws_folder}/{test_file_name}")

    # List folder / files
    root_dir = storage_adaptor.list("")
    assert f"{aws_folder}/" in root_dir

    listed_files = storage_adaptor.list(aws_folder)
    assert f"{aws_folder}/{test_file_name}" in listed_files

    # Load file
    test_file_path = f"tests/test_data/downloaded_test_file.txt"
    storage_adaptor.load(f"{aws_folder}/{test_file_name}", test_file_path)
    with open(test_file_path, "r") as f:
        assert f.read() == "test file content"
