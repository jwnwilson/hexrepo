import json
import os
import subprocess
from contextlib import chdir
from typing import List, Optional, Set

import typer

from .system import run_system_command


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
    adaptor_folder = "libs/adaptor"
    interactor_folder = "libs/interactor"
    return scan_folder(adaptor_folder) + scan_folder(interactor_folder)


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
    library_type: str = get_library_type(library)
    modified_files = get_modified_files()
    if f"libs/{library_type}/{library}" in modified_files:
        pyproject_diff: str = subprocess.getoutput(
            f"git diff origin/main HEAD libs/{library_type}/{library}/pyproject.toml"
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
        lib_type = get_library_type(lib)
        if f"libs/{lib_type}/{lib}" in modified_files:
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


def get_library_type(library: str) -> str:
    adaptor_folder = "libs/adaptor"
    interactor_folder = "libs/interactor"
    if library in scan_folder(adaptor_folder):
        return "adaptor"
    elif library in scan_folder(interactor_folder):
        return "interactor"
    else:
        raise RuntimeError(f"Library {library} not found")


def install_library_in_project(library: str, project: str):
    # Install library locally in uv dev group
    libraries: List[str] = get_libraries()
    projects: List[str] = get_projects()

    assert project in projects, f"Project {project} not found"
    assert library in libraries, f"Library {library} not found"

    library_type = get_library_type(library)
    with chdir(f"projects/{project}"):
        run_system_command(f"uv add --editable ../../libs/{library_type}/{library}")
    typer.echo(f"Library {library} installed in project {project}")
