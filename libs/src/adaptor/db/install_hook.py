import os
import logging

from tools.logic.project import run_system_command

logger = logging.getLogger(__name__)

# Source : destination
copy_folders_files = {
    "monorepo_db/sql/alembic": "src/app/adaptor/db/sql",
    "monorepo_db/sql/models": "src/app/adaptor/db/sql"

}

def copy_boilerplate_code_to_project(project_path: str):
    # Need to ensure this is run from the lib path
    for source in copy_folders_files:
        destination = copy_folders_files[source]
        logger.info(f"Copying {source} to {project_path}/{destination}")
        run_system_command(f"cp -r {source} {project_path}/{destination}")
        

if __name__ == "__main__":
    copy_boilerplate_code_to_project()