import os

import boto3
import typer


def create_aws_bucket(bucket_name: str) -> None:
    try:
        # Create S3 bucket
        client = boto3.client(
            's3',
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        )
        client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': os.environ["AWS_DEFAULT_REGION"]})
    except Exception as err:
        if "BucketAlreadyOwnedByYou" in str(err):
            typer.echo(f"Bucket {bucket_name} already exists, skipping...")
        elif "The specified bucket is not valid." in str(err):
            typer.echo("""The bucket name can be between 3 and 63 characters long, and can contain only lower-case characters, numbers, periods, and dashes.

    Each label in the bucket name must start with a lowercase letter or number.

    The bucket name cannot contain underscores, end with a dash, have consecutive periods, or use dashes adjacent to periods.
            
    Please update AWS_TF_STATE_BUCKET env var in your shell file and try again.""")
            raise typer.Abort()
        else:
            typer.echo(f"Error creating bucket: {err}")
            raise typer.Abort()
    