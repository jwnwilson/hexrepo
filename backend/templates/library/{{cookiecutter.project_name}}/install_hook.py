import os
import logging

logger = logging.getLogger(__name__)

# Source : destination
copy_folders_files = {

}

def copy_boilerplate_code_to_project(project_path: str):
    for source in copy_folders_files:
        destination = copy_folders_files[source]
        logger.infio(f"Copying {source} to {project_path}/{destination}")
        os.system(f"cp -r {source} {project_path}/{destination}")
        

if __name__ == "__main__":
    copy_boilerplate_code_to_project()