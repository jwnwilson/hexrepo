import json
import subprocess
import boto3
import os

import typer

from tools.logic.env import set_env_var


def create_tf_state(cloud_provider: str) -> None:
    if cloud_provider == "aws":
        # Prompt for bucket name
        bucket_name: str = os.environ.get("AWS_TF_STATE_BUCKET")
        # Attempt to create bucket
        try:
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
        typer.echo(f"Bucket {bucket_name} created successfully.")


def create_lib_infra(shell_file: str) -> None:
    typer.echo("Creating infrastructure for libraries...")
    # Placeholder for library infra setup
    os.chdir("backend/libs")
    os.system("make tf_init")
    os.system("make tf_plan")
    os.system("make tf_apply")
    # Save lib repo url to env var
    tf_output = subprocess.check_output(["make", "tf_output"])
    repo_url: str = json.loads(tf_output)["aws_codeartifact_repository_endpoint"]["value"]
    set_env_var(shell_file, "MONOREPO_LIB_REPO_URL", repo_url)
    typer.echo("Infrastructure setup complete.")


def publish_libs() -> None:
    typer.echo("Publishing libraries to repo...")
    # Get code repo token
    # Publish all libraries
    # Placeholder for publishing libraries to repo
    typer.echo("Libraries published successfully.")
