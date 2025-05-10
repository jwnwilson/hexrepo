import os
import shutil
from pathlib import Path
import pytest

from copier.main import Worker

from .utils import copy_project_dependencies


@pytest.fixture
def template_path():
    """Return the path to the template directory."""
    return Path(__file__).parent.parent.parent.parent / "templates" / "library"


@pytest.fixture
def tmp_library_path(tmp_path):
    """Create a temporary directory for the library."""
    library_path = tmp_path / "test_library"
    yield library_path
    # Cleanup after test
    if library_path.exists():
        shutil.rmtree(library_path)


def test_copy_library(template_path, tmp_library_path):
    """Test basic library generation."""
    # Run copier copy
    worker = Worker(
        src_path=str(template_path),
        dst_path=str(tmp_library_path),
        data={
            "project_name": "test_library",
            "description": "Test library",
            "full_name": "Test User",
        },
        defaults=True
    )
    worker.run_copy()

    # Verify the library was created
    assert tmp_library_path.exists()
    assert tmp_library_path.is_dir()
    assert (tmp_library_path / "pyproject.toml").exists()


def test_copy_then_run_library_tests(template_path, tmp_library_path):
    """Test library generation and running tests."""
    # Run copier copy
    worker = Worker(
        src_path=str(template_path),
        dst_path=str(tmp_library_path),
        data={
            "project_name": "test_library",
            "description": "Test library",
            "full_name": "Test User",
        },
        defaults=True
    )
    worker.run_copy()

    # Copy required tools efficiently
    copy_project_dependencies(template_path.parent.parent, tmp_library_path, components=['tools'], lib=True)

    # Run tests
    exit_code = os.system(f"cd {tmp_library_path} && make test")
    assert exit_code == 0, "Error running: make test didn't run successfully in new copier library" 
