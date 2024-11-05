import pytest 
from storage.aws import S3Adaptor
from storage.interface import StorageConfig


@pytest.fixture
def aws_config() -> StorageConfig:
    return StorageConfig(
        aws_auth={
            "user": "test-user",
            "upload_user_access_id": "test-access-id",
            "upload_user_secret_key": "test-secret"
        },
        aws_bucket="test-bucket",
        aws_upload_prefix="test-upload-prefix"
    )


@pytest.fixture
def clear_test_folder(aws_config: StorageConfig):
    storage_adaptor = S3Adaptor(storage_config=aws_config)
    storage_adaptor.delete("test_folder")


@pytest.mark.e2e
def test_aws_storage_e2e(aws_config: StorageConfig, clear_test_folder):
    # Assert credentials are set
    storage_adaptor = S3Adaptor(aws_config)

    # Create folder
    storage_adaptor.create_folder("test_folder")

    # Save file
    with open("test_file.txt", "w") as f:
        f.write("test file content")
    
    storage_adaptor.save("test_folder", "test_file.txt")

    # List folder / files
    root_dir = storage_adaptor.list("")
    assert "test_folder" in root_dir

    test_folder = storage_adaptor.list("test_folder")
    assert "test_file.txt" in test_folder

    # Load file
    content = storage_adaptor.load("test_folder/test_file.txt")
    assert content == "test file content"
