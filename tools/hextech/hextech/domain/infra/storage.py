import typer
from monorepo_cloud.storage import S3Adaptor

from hextech.config import MonorepoConfig


def create_bucket(bucket_name: str, config: MonorepoConfig) -> None:
    if config.cloud_provider == "aws":
        try:
            S3Adaptor.create_bucket(bucket_name, config.cloud_provider_config)
        except Exception as err:
            typer.echo(f"Error creating bucket: {err}")


def create_tf_state(config: MonorepoConfig) -> None:
    # Prompt for bucket name
    bucket_name: str = config.cloud_provider_config.AWS_TF_STATE_BUCKET
    # Attempt to create bucket
    create_bucket(bucket_name, config)
    typer.echo(f"Bucket {bucket_name} created successfully.")
