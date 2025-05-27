import json
import subprocess
from contextlib import chdir
from typing import Dict, List, Optional

import typer

from hextech.config import HexrepoConfig
from hextech.domain.infra.bastion import db_exists, managed_bastion_ssh
from hextech.domain.infra.code_repo import authenticate_lib_repo
from hextech.domain.project import (
    find_repo_root,
    get_libraries,
    get_library_type,
    get_modified_libraries,
    get_modified_projects,
    get_projects,
    get_projects_usings_libraries,
    build_push_deploy
)
from hextech.domain.system import run_system_command, run_system_command_with_output


def create_shared_infra(config: HexrepoConfig) -> None:
    typer.echo("Creating initial hexrepo infrastructure...")
    project_root: str = find_repo_root()

    # Placeholder for library infra setup
    with chdir(project_root):
        with chdir("infra"):
            run_system_command("make tf_shared_init")
            run_system_command("make tf_shared_apply")
            code_repo_data = subprocess.getoutput("make tf_shared_output")
            code_repo_url = json.loads(code_repo_data)[
                "aws_codeartifact_repository_endpoint"
            ]["value"]
    config.set_config_var("hexrepo_lib_repo_url", code_repo_url, set_env=True)
    typer.echo("Infrastructure setup complete.")


def destroy_shared_infra(config: HexrepoConfig, no_input: bool = False) -> None:
    typer.echo("Destroying shared infrastructure...")
    project_root: str = find_repo_root()
    with chdir(project_root):
        with chdir("infra"):
            run_system_command("make tf_shared_destroy")
    typer.echo("Shared infrastructure destroyed.")


def publish_libs(
    config: HexrepoConfig,
    libraries: Optional[List[str]] = None,
    check_modified: bool = False,
) -> None:
    typer.echo("Publishing libraries to repo...")
    project_root: str = find_repo_root()
    with chdir(project_root):
        # Get code repo token
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
            with chdir(f"libs/{lib_type}/{lib}"):
                run_system_command(
                    f"make publish HEXREPO_LIB_REPO_URL={config.hexrepo_lib_repo_url}"
                )
    # Placeholder for publishing libraries to repo
    typer.echo("Libraries published successfully.")


def deploy_projects(
    env: str,
    config: HexrepoConfig,
    projects: Optional[List[str]],
    check_modified: bool = False,
    no_input: bool = False,
) -> None:
    typer.echo(f"Publishing projects: {projects}...")
    project_root: str = find_repo_root()
    with chdir(project_root):
        # Publish all libraries if none specified
        projects = projects if projects else get_projects()

        if check_modified:
            libraries = get_modified_libraries()
            projects_with_modified_libs = get_projects_usings_libraries(libraries)
            projects = set(
                projects_with_modified_libs + get_modified_projects(projects)
            )

        if not projects:
            typer.echo("No modified files found, skipping deploy.")
            return

        for proj in projects:
            with chdir(f"projects/{proj}"):
                typer.echo(f"Deploying project {proj}...")
                run_system_command("make tf_init")
                # Build, push images and deploy
                build_push_deploy()

    # Placeholder for publishing libraries to repo
    typer.echo("Projects deployed successfully.")


def create_per_env_infra(config: HexrepoConfig) -> None:
    typer.echo("Setting up per env infrastructure...")
    project_root: str = find_repo_root()
    with chdir(project_root):
        # Placeholder for shared infra setup
        with chdir("infra"):
            run_system_command("make tf_env_init ENV=dev")
            for env in config.environments:
                try:
                    run_system_command(f"ENVIRONMENT={env} make tf_workspace")
                except:  # noqa
                    pass
                # run_system_command(f"make tf_env_plan ")
                run_system_command("make tf_env_apply ")
    typer.echo("Shared infrastructure setup complete.")


def shared_infra_plan_command(config: HexrepoConfig) -> None:
    typer.echo("Planning shared infrastructure...")
    project_root: str = find_repo_root()
    with chdir(project_root):
        with chdir("infra"):
            run_system_command("make tf_shared_init")
            run_system_command("make tf_shared_plan")
    typer.echo("Shared infrastructure plan complete.")


def shared_infra_apply_command(config: HexrepoConfig, no_input: bool = False) -> None:
    typer.echo("Applying shared infrastructure...")
    project_root: str = find_repo_root()
    with chdir(project_root):
        with chdir("infra"):
            run_system_command("make tf_shared_init")
            if no_input:
                run_system_command("make tf_shared_apply_no_input")
            else:
                run_system_command("make tf_shared_apply")
    typer.echo("Shared infrastructure apply complete.")


def plan_env_infra_command(config: HexrepoConfig, env: str) -> None:
    typer.echo("Planning shared infrastructure...")
    project_root: str = find_repo_root()
    with chdir(project_root):
        with chdir("infra"):
            run_system_command("make tf_env_init")
            try:
                run_system_command(f"ENVIRONMENT={env} make tf_workspace")
            except:  # noqa
                pass
            run_system_command("make tf_env_plan")
    typer.echo("Shared infrastructure plan complete.")


def create_env_infra(config: HexrepoConfig, env: str, no_input: bool = False) -> None:
    typer.echo("Applying shared infrastructure...")
    project_root: str = find_repo_root()
    with chdir(project_root):
        with chdir("infra"):
            run_system_command("make tf_env_init")
            try:
                run_system_command(f"ENVIRONMENT={env} make tf_workspace")
            except:  # noqa
                pass
            if no_input:
                run_system_command("make tf_env_apply_no_input")
            else:
                run_system_command("make tf_env_apply")
    typer.echo("Shared infrastructure apply complete.")


def destroy_env_infra(config: HexrepoConfig, env: str) -> None:
    typer.echo("Destroying shared infrastructure...")
    project_root: str = find_repo_root()
    with chdir(project_root):
        with chdir("infra"):
            run_system_command("make tf_env_init")
            try:
                run_system_command(f"ENVIRONMENT={env} make tf_workspace")
            except:  # noqa
                pass
            run_system_command("make tf_env_destroy")
    typer.echo("Shared infrastructure destroyed.")


def get_terrform_output(env: str, project: str) -> str:
    project_root: str = find_repo_root()
    with chdir(project_root):
        run_system_command(
            f"cd projects/{project} && make tf_init && make tf_refresh ENVIRONMENT={env}"
        )
        tf_str: str = run_system_command_with_output(
            f"cd projects/{project} && make --no-print-directory tf_output ENVIRONMENT={env}"
        )
        typer.echo("Loading Terraform output")
        try:
            return json.loads(tf_str)
        except json.JSONDecodeError as err:
            raise typer.Abort(f"Error parsing terraform output: {err}")


def migrate_db(config: HexrepoConfig, env: str, project: str):
    project_root: str = find_repo_root()
    with chdir(project_root):
        if config.cloud_provider == "aws" and env != "local":
            if not db_exists(config, project, env):
                typer.echo(
                    f"DB not found for project {project} in environment {env}, skipping migration"
                )
                return
            # Start bastion
            with managed_bastion_ssh(config, env, project):
                try:
                    tf_output: Dict[str, str] = get_terrform_output(env, project)
                    secret_name = tf_output["db_secret_name"]["value"]
                    db_url = (
                        "postgresql+psycopg://postgres:{password}@127.0.0.1:5432/"
                        + project
                    )

                    # Run migration with secret name set
                    # stop making docker db call
                    typer.echo(f"Running migration for project {project}")
                    run_system_command(
                        f"""
                        cd projects/{project} && \
                        make --no-print-directory db_migrate_pipeline \
                        DB_PASSWORD_SECRET_NAME={secret_name} DB_URL={db_url} DB_RO_URL={db_url} CLOUD_PROVIDER={config.cloud_provider} SESSION_SECRET=secret
                    """
                    )
                except Exception as err:
                    typer.echo(f"Error running migration: {err}")
                    raise typer.Abort()

        elif env == "local":
            typer.echo("Running migration locally")
            run_system_command(
                f"cd projects/{project} && make --no-print-directory db_migrate_local"
            )
