
from contextlib import chdir
import os
import subprocess
from typing import List, Set

import typer


def scan_folder(folder: str) -> List[str]:
    return [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]


def get_projects() -> List[str]:
    project_folder = "projects"
    return scan_folder(project_folder)


def get_libraries()-> List[str]:
    adaptor_folder = "libs/src/adaptor"
    interactor_folder = "libs/src/interactor"
    return scan_folder(adaptor_folder) + scan_folder(interactor_folder)


def get_modified_libraries(libraries: List[str]) -> List[str]:
    modified_libs: List[str] = []
    modified_files = subprocess.getoutput("git diff --name-only")
    for lib in libraries:
        lib_type = get_library_type(lib)
        if f"libs/src/{lib_type}/{lib}" in modified_files:
            modified_libs.append(lib)
    return modified_libs


def get_modified_projects(projects: List[str]) -> List[str]:
    modified_projects: List[str] = []
    modified_files = subprocess.getoutput("git diff --name-only")
    for proj in projects:
        if f"projects/{proj}" in modified_files:
            modified_projects.append(proj)
    return modified_projects


def get_projects_usings_libraries(libraries: List[str]) -> List[str]:
    breakpoint()
    projects: List[str] = get_projects()
    projects_using_libs: Set[str] = {}
    for proj in projects:
        with chdir(f"projects/{proj}"):
            for lib in libraries:
                with open("pyproject.toml") as f:
                    if f"monorepo_{lib}" in f.read():
                        projects_using_libs.add(proj)
    return list(projects_using_libs)


def get_library_type(library: str) -> str:
    adaptor_folder = "libs/src/adaptor"
    interactor_folder = "libs/src/interactor"
    if library in scan_folder(adaptor_folder):
        return "adaptor"
    elif library in scan_folder(interactor_folder):
        return "interactor"
    else:
        raise RuntimeError(f"Library {library} not found")
    

def install_library_in_project(library: str, project: str):
    # Install library locally in poetry dev group
    libraries: List[str] = get_libraries()
    projects: List[str] = get_projects()

    assert project in projects, f"Project {project} not found"
    assert library in libraries, f"Library {library} not found"

    library_type = get_library_type(library)
    with chdir(f"projects/{project}"):
        os.system(f"poetry add --editable ../../libs/src/{library_type}/{library} -G dev")
        os.system(f"poetry add {library} -G prod")
    typer.echo(f"Library {library} installed in project {project}")
