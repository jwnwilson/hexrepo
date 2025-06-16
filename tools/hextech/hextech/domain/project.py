import functools
import json
import logging
import os
import subprocess
from contextlib import chdir
from typing import List, Optional, Set

import typer
import yaml

from .system import run_system_command

logger = logging.getLogger(__name__)


def cli_setup(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check if .hexroot file exists
        find_repo_root()
        return func(*args, **kwargs)

    return wrapper


def find_repo_root() -> str:
    try:
        # search this active directory for .hexroot file
        current_dir = os.getcwd()
        if os.path.isfile(".hexroot"):
            return current_dir
        else:
            # if not found go up one directory search parent directory
            os.chdir("..")
            return find_repo_root()
    except Exception:
        typer.echo("Unable to find .hexroot file, aborting.")
        raise typer.Abort()


def scan_folder(folder: str) -> List[str]:
    return [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]


def get_environments():
    try:
        with open("config.json") as f:
            return json.loads(f.read())["environments"]
    except Exception as err:
        raise typer.Abort(f"Error reading environments from config.json: {err}")


def get_projects() -> List[str]:
    project_folder = "projects"
    return scan_folder(project_folder)


def get_libraries() -> List[str]:
    libs_folder = "libs"
    return scan_folder(libs_folder)


def validate_libraries(libraries: Optional[List[str]] = None) -> List[str]:
    repo_libs: List[str] = get_libraries()
    if libraries and "" in libraries:
        libraries = libraries.remove("")

    if not libraries:
        libraries: List[str] = get_libraries()
    else:
        assert all(
            lib in repo_libs for lib in libraries
        ), "Invalid library name provided"
    return libraries


def get_modified_files() -> str:
    current_branch = subprocess.getoutput("git branch --show-current")
    if current_branch != "main":
        return subprocess.getoutput(
            "git fetch --unshallow origin main && git diff origin/main HEAD --name-only"
        )
    else:
        return subprocess.getoutput(
            "git fetch && git diff origin/main HEAD^ --name-only"
        )


def library_version_bump_required(library: str) -> bool:
    modified_files = get_modified_files()
    if f"libs/{library}" in modified_files:
        pyproject_diff: str = subprocess.getoutput(
            f"git diff origin/main HEAD libs/{library}/pyproject.toml"
        )
        if "version = " in pyproject_diff:
            return False
        return True
    return False


def get_modified_libraries(libraries: Optional[List[str]] = None) -> List[str]:
    libraries = libraries or get_libraries()
    modified_libs: List[str] = []
    modified_files = get_modified_files()
    for lib in libraries:
        if f"libs/{lib}" in modified_files:
            modified_libs.append(lib)
    return modified_libs


def get_modified_projects(projects: List[str]) -> List[str]:
    modified_projects: List[str] = []
    modified_files = get_modified_files()
    for proj in projects:
        if f"projects/{proj}" in modified_files:
            modified_projects.append(proj)
    return modified_projects


def get_projects_usings_libraries(libraries: List[str]) -> List[str]:
    projects: List[str] = get_projects()
    projects_using_libs: Set[str] = {}
    for proj in projects:
        with chdir(f"projects/{proj}"):
            for lib in libraries:
                with open("pyproject.toml") as f:
                    if f"hexrepo_{lib}" in f.read():
                        projects_using_libs.add(proj)
    return list(projects_using_libs)


def install_library_in_project(library: str, project: str):
    # Install library locally in uv dev group
    libraries: List[str] = get_libraries()
    projects: List[str] = get_projects()

    assert project in projects, f"Project {project} not found"
    assert library in libraries, f"Library {library} not found"

    with chdir(f"projects/{project}"):
        run_system_command(f"uv add --editable ../../libs/{library}")
    typer.echo(f"Library {library} installed in project {project}")


def build_push_deploy(env: str, project: str):
    # Load project config
    with open("hexproject.yaml") as f:
        project_config = yaml.safe_load(f)

    # Build images
    run_system_command("make build")

    docker_tag: str = subprocess.getoutput(
        "git log -n1 --pretty='format:%cd' --date=format:'%Y%m%d%H%M%S'"
    )

    # Push images
    for deployment in project_config["deployments"]:
        container_image = deployment["container_image"]
        image_type = deployment["image_type"]
        typer.echo(f"Building and pushing image {container_image}:{docker_tag}")
        run_system_command(
            f"IMAGE={container_image} DOCKER_TAG={docker_tag} ../../tools/bash_scripts/push_image.sh"
        )

    # Deploy images
    for deployment in project_config["deployments"]:
        container_image = deployment["container_image"]
        image_type = deployment["image_type"]
        targets: list[str] = deployment["targets"]
        targets_command: list[str] = " ".join(
            [f"--target={target}" for target in targets]
        )
        typer.echo(f"Deploying image {container_image}:{docker_tag}")
        if image_type == "container":
            run_system_command(
                f"DOCKER_TAG_CONTAINER={docker_tag} TARGETS='{targets_command}' NO_INPUT=True ../../tools/bash_scripts/deploy.sh"
            )
        elif image_type == "serverless":
            run_system_command(
                f"DOCKER_TAG_SERVERLESS={docker_tag} TARGETS='{targets_command}' NO_INPUT=True ../../tools/bash_scripts/deploy.sh"
            )

    # Save docker tags to S3
    typer.echo(f"Saving docker tags to S3: {docker_tag}")
    save_docker_tags(env, project, docker_tag)


def get_docker_tags(env: str, project: str) -> dict[str, str]:
    from hexrepo_cloud.config import AWSConfig, load_aws_config
    from hexrepo_cloud.storage.aws import S3Adaptor, StorageConfig

    # get docker tags from S3 file
    try:
        aws_config: AWSConfig = load_aws_config()
        s3_file: str = f"{project}/{env}/docker_tags.json"
        storage_adaptor = S3Adaptor(
            StorageConfig(aws_bucket="hexrepo-infra", aws_region=aws_config.AWS_REGION)
        )
        docker_tags: dict[str, str] = json.loads(storage_adaptor.read(s3_file))
    except Exception as err:
        logger.error(
            f"Error reading docker tags from S3, defaulting to latest tags: {err}"
        )
        return {"container": "latest", "serverless": "latest"}
    return docker_tags


def save_docker_tags(env: str, project: str, docker_tag: str):
    from hexrepo_cloud.config import AWSConfig, load_aws_config
    from hexrepo_cloud.storage.aws import S3Adaptor, StorageConfig

    try:
        aws_config: AWSConfig = load_aws_config()
        s3_file: str = f"{project}/{env}/docker_tags.json"
        storage_adaptor = S3Adaptor(
            StorageConfig(aws_bucket="hexrepo-infra", aws_region=aws_config.AWS_REGION)
        )
        tags: dict[str, str] = {"container": docker_tag, "serverless": docker_tag}
        storage_adaptor.write(s3_file, json.dumps(tags))
        typer.echo(f"Docker tags saved to S3: {s3_file}")
    except Exception as err:
        logger.error(f"Error saving docker tags to S3: {err}")
        raise typer.Abort(f"Error saving docker tags to S3: {err}")
