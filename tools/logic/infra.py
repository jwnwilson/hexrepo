from contextlib import chdir
import json
import subprocess
from typing import List, Optional
import os

import typer

from tools.logic.aws.auth import authenticate_lib_repo
from tools.logic.aws.s3 import create_aws_bucket
from tools.logic.config import MonorepoConfig
from tools.logic.project import get_libraries, get_library_type, get_modified_libraries, get_modified_projects, get_projects, get_projects_usings_libraries
from tools.logic.commands import run_system_command


def create_tf_state(config: MonorepoConfig) -> None:
    if config.cloud_provider == "aws":
        # Prompt for bucket name
        bucket_name: str = config.cloud_provider_config.AWS_TF_STATE_BUCKET
        # Attempt to create bucket
        create_aws_bucket(bucket_name)
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
    with chdir("libs"):
        run_system_command("make tf_shared_init")
        run_system_command("make tf_shared_apply")
        code_repo_data = subprocess.getoutput("make tf_shared_output")
        code_repo_url = json.loads(code_repo_data)["aws_codeartifact_repository_endpoint"]["value"]
        config.set_config_var("monorepo_lib_repo_url", code_repo_url, set_env=True)
    typer.echo("Infrastructure setup complete.")


def publish_libs(config: MonorepoConfig, libraries: Optional[List[str]] = None, check_modified: bool = False) -> None:
    typer.echo("Publishing libraries to repo...")
    # Get code repo token
    assert os.environ.get("MONOREPO_LIB_REPO_URL"), "Library repo url not found."
    authenticate_lib_repo(config)
    # Publish all libraries if none specified
    libraries = libraries if libraries else get_libraries()

    if check_modified:
        libraries = get_modified_libraries(libraries)

    if not libraries:
        typer.echo("No modified files found, skipping publish.")
        return

    for lib in libraries:
        lib_type = get_library_type(lib)
        with chdir(f"libs/src/{lib_type}/{lib}"):
            run_system_command("make publish")
    # Placeholder for publishing libraries to repo
    typer.echo("Libraries published successfully.")


def deploy_projects(config: MonorepoConfig, projects: Optional[List[str]], check_modified: bool = False) -> None:
    typer.echo("Publishing projects to repo...")
    # Get code repo token
    assert os.environ.get("MONOREPO_LIB_REPO_URL"), "Library repo url not found."
    authenticate_lib_repo(config)
    # Publish all libraries if none specified
    projects = projects if projects else get_projects()

    if check_modified:
        libraries = get_modified_libraries()
        projects_with_modified_libs = get_projects_usings_libraries(libraries)
        projects = set(projects_with_modified_libs + get_modified_projects(projects))

    if not projects:
        typer.echo("No modified files found, skipping deploy.")
        return

    for proj in projects:
        with chdir(f"projects/{proj}"):
            run_system_command("make deploy")
    # Placeholder for publishing libraries to repo
    typer.echo("Projects deployed successfully.")


def setup_global_env_infra(config: MonorepoConfig) -> None:
    typer.echo("Setting up global env infrastructure...")
    # Placeholder for shared infra setup
    with chdir("libs"):
        run_system_command(f"make tf_env_init ENV=dev")
        for env in config.environments:
            run_system_command(f"ENVIRONMENT={env} make tf_workspace")
            # run_system_command(f"make tf_env_plan ")
            run_system_command(f"make tf_env_apply ")
    typer.echo("Shared infrastructure setup complete.")


def infra_plan(config: MonorepoConfig) -> None:
    typer.echo("Planning shared infrastructure...")
    with chdir("libs"):
        run_system_command("make tf_shared_init")
        run_system_command("make tf_shared_plan")
    typer.echo("Shared infrastructure plan complete.")


def infra_apply(config: MonorepoConfig) -> None:
    typer.echo("Applying shared infrastructure...")
    with chdir("libs"):
        run_system_command("make tf_shared_init")
        run_system_command("make tf_shared_apply")
    typer.echo("Shared infrastructure apply complete.")
