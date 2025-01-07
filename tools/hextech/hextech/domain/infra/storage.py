import typer
from hexrepo_cloud.storage import S3Adaptor
from hexrepo_cloud.db.aws import DynamoDBManager

from hextech.config import HexrepoConfig


def create_tf_bucket(bucket_name: str, config: HexrepoConfig) -> None:
    if config.cloud_provider == "aws":
        try:
            if not S3Adaptor.bucket_exists(bucket_name, config.cloud_provider_config):
                S3Adaptor.create_bucket(bucket_name, config.cloud_provider_config)
            else:
                typer.echo(f"Bucket {bucket_name} already exists, skipping.")
        except Exception as err:
            typer.echo(f"Error creating bucket: {err}")


def create_tf_lock(table_name: str, config: HexrepoConfig) -> None:
    if config.cloud_provider == "aws":
        try:
            db_manager = DynamoDBManager(config.cloud_provider_config)
            if not db_manager.table_exists(table_name):
                db_manager.create_table(
                    table_name,
                    key_schema=[{"AttributeName": "LockID", "KeyType": "HASH"}],
                    attr_definitions=[{"AttributeName": "LockID", "AttributeType": "S"}]
                )
            else:
                typer.echo(f"Table {table_name} already exists, skipping.")
        except Exception as err:
            typer.echo(f"Error creating table: {err}")


def create_tf_state(config: HexrepoConfig) -> None:
    # Prompt for bucket name
    bucket_name: str = config.cloud_provider_config.AWS_TF_STATE_BUCKET
    # Attempt to create bucket
    create_tf_bucket(bucket_name, config)
    create_tf_lock("terraform-state-lock-dynamo", config)
    typer.echo(f"Bucket {bucket_name} created successfully.")
