from contextlib import chdir
import json
import signal
import subprocess
from typing import Dict, List, Optional
import os

import typer

from hexcli.domain.infra.code_repo import authenticate_lib_repo
from hexcli.config import MonorepoConfig
from hexcli.domain.project import get_libraries, get_library_type, get_modified_libraries, get_modified_projects, get_projects, get_projects_usings_libraries
from hexcli.domain.system import run_system_command, run_system_command_with_output
from hexcli.domain.infra.bastion import bastion_ssh_tunnel


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


def deploy_projects(env: str, config: MonorepoConfig, projects: Optional[List[str]], check_modified: bool = False, no_input: bool = False) -> None:
    typer.echo("Publishing projects to repo...")
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
            run_system_command(f"make deploy ENV={env} NO_INPUT=${no_input}")
    # Placeholder for publishing libraries to repo
    typer.echo("Projects deployed successfully.")


def setup_global_env_infra(config: MonorepoConfig) -> None:
    typer.echo("Setting up global env infrastructure...")
    # Placeholder for shared infra setup
    with chdir("libs"):
        run_system_command(f"make tf_env_init ENV=dev")
        for env in config.environments:
            try:
                run_system_command(f"ENVIRONMENT={env} make tf_workspace")
            except:
                pass
            # run_system_command(f"make tf_env_plan ")
            run_system_command(f"make tf_env_apply ")
    typer.echo("Shared infrastructure setup complete.")


def shared_infra_plan_command(config: MonorepoConfig) -> None:
    typer.echo("Planning shared infrastructure...")
    with chdir("libs"):
        run_system_command("make tf_shared_init")
        run_system_command("make tf_shared_plan")
    typer.echo("Shared infrastructure plan complete.")


def shared_infra_apply_command(config: MonorepoConfig) -> None:
    typer.echo("Applying shared infrastructure...")
    with chdir("libs"):
        run_system_command("make tf_shared_init")
        run_system_command("make tf_shared_apply")
    typer.echo("Shared infrastructure apply complete.")


def env_infra_plan_command(config: MonorepoConfig, env: str) -> None:
    typer.echo("Planning shared infrastructure...")
    with chdir("libs"):
        run_system_command("make tf_env_init")
        try:
            run_system_command(f"ENVIRONMENT={env} make tf_workspace")
        except:
            pass
        run_system_command("make tf_env_plan")
    typer.echo("Shared infrastructure plan complete.")


def env_infra_apply_command(config: MonorepoConfig, env: str) -> None:
    typer.echo("Applying shared infrastructure...")
    with chdir("libs"):
        run_system_command("make tf_env_init")
        try:
            run_system_command(f"ENVIRONMENT={env} make tf_workspace")
        except:
            pass
        run_system_command("make tf_env_apply")
    typer.echo("Shared infrastructure apply complete.")


def get_terrform_output(env: str, project: str) -> str:
    run_system_command(f"cd projects/{project} && make tf_refresh ENVIRONMENT={env}")
    tf_str: str = run_system_command_with_output(f"cd projects/{project} && make --no-print-directory tf_output ENVIRONMENT={env}")
    typer.echo(f"Terraform output: '{tf_str}'")
    try:
        return json.loads(tf_str)
    except json.JSONDecodeError as err:
        raise typer.Abort(f"Error parsing terraform output: {err}")


def migrate_db(config: MonorepoConfig, env: str, project: str):
    if config.cloud_provider == "aws":
        # Start bastion
        typer.echo(f"Starting ssh tunnel to bastion")
        bastion_process = bastion_ssh_tunnel(config, env, project, background_task=True)
        try:
            # Get secret name
            secret_name: str = ""
            db_url: str = ""
            if env != "local":
                tf_output: Dict[str, str] = get_terrform_output(env, project)
                secret_name = tf_output["db_secret_name"]["value"]
                db_url = "postgresql+psycopg2://postgres:{password}@127.0.0.1:5432/" + project

            # Run migration with secret name set
            # stop making docker db call
            typer.echo(f"Running migration for project {project}")
            run_system_command(f"""
                cd projects/{project} && \
                make --no-print-directory db_migrate DB_PASSWORD_SECRET_NAME={secret_name} DB_URL={db_url} CLOUD_PROVIDER={config.cloud_provider}
            """)
        except Exception as err:
            typer.echo(f"Error running migration: {err}")
        finally:
            # Terminate bastion
            typer.echo(f"Shutting down ssh tunnel to bastion")
            os.killpg(os.getpgid(bastion_process.pid), signal.SIGTERM)
