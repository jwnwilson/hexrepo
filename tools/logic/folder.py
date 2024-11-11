
import os
from typing import List


def scan_folder(folder: str) -> List[str]:
    return [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]


def get_projects() -> List[str]:
    project_folder = "backand/projects"
    return scan_folder(project_folder)


def get_libraries()-> List[str]:
    adaptor_folder = "backand/libs/src/adaptor"
    interactor_folder = "backand/libs/src/interactor_folder"
    return scan_folder(adaptor_folder) + scan_folder(interactor_folder)


def get_library_type(library: str) -> str:
    adaptor_folder = "backand/libs/src/adaptor"
    interactor_folder = "backand/libs/src/interactor_folder"
    if library in scan_folder(adaptor_folder):
        return "adaptor"
    elif library in scan_folder(interactor_folder):
        return "interactor"
    else:
        raise RuntimeError(f"Library {library} not found")