from contextlib import chdir
import json
import subprocess
import boto3
import os

import typer

from tools.logic.auth import authenticate_lib_repo
from tools.logic.config import MonorepoConfig
from tools.logic.env import set_env_var
from tools.logic.project import get_libraries, get_library_type


def create_tf_state(config: MonorepoConfig) -> None:
    if config.cloud_provider == "aws":
        # Prompt for bucket name
        bucket_name: str = config.cloud_provider_config.AWS_TF_STATE_BUCKET
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


def authenticate_cloud(config: MonorepoConfig) -> None:
    typer.echo("Authenticating with cloud provider...")
     # Save lib repo url to env var
    if config.cloud_provider == "aws":
        authenticate_lib_repo(config)
    typer.echo("Authentication successful.")


def create_lib_infra(config: MonorepoConfig) -> None:
    typer.echo("Creating infrastructure for libraries...")
    # Placeholder for library infra setup
    with chdir("backend/libs"):
        os.system("make tf_shared_init")
        os.system("make tf_shared_plan")
        os.system("make tf_shared_apply")
    typer.echo("Infrastructure setup complete.")


def publish_libs(config: MonorepoConfig) -> None:
    typer.echo("Publishing libraries to repo...")
    # Get code repo token
    assert os.environ.get("MONOREPO_LIB_REPO_URL"), "Library repo url not found."
    authenticate_lib_repo(config)
    # Publish all libraries
    for lib in get_libraries():
        lib_type = get_library_type(lib)
        with chdir(f"backend/libs/src/{lib_type}/{lib}"):
            os.system("make publish")
    # Placeholder for publishing libraries to repo
    typer.echo("Libraries published successfully.")


def setup_global_env_infra(config: MonorepoConfig) -> None:
    typer.echo("Setting up global env infrastructure...")
    # Placeholder for shared infra setup
    with chdir("backend/libs"):
        os.system(f"make tf_env_init ENV=dev")
        for env in config.environments:
            os.system(f"ENVIRONEMNT={env} make tf_env_plan ")
            os.system(f"ENVIRONEMNT={env} make tf_env_apply ")
    typer.echo("Shared infrastructure setup complete.")
