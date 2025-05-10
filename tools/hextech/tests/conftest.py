import os
import subprocess
import sys
from unittest import mock
import pytest
from pathlib import Path


@pytest.fixture
def update_path_project():
    repo_root_dir: str = Path(os.getcwd()).parent.parent.absolute()
    project_dir: str = str(repo_root_dir / "templates" / "project")
    sys.path.append(project_dir)
    yield
    sys.path.remove(project_dir)


@pytest.fixture
def update_path_libs():
    repo_root_dir: str = Path(os.getcwd()).parent.parent.absolute()
    project_dir: str = str(repo_root_dir / "templates" / "libs")
    sys.path.append(project_dir)
    yield
    sys.path.remove(project_dir)

