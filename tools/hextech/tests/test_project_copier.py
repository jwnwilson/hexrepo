import os
import shutil
from pathlib import Path
import pytest
from copier import run_copy
from copier.main import Worker


@pytest.fixture
def template_path():
    """Return the path to the template directory."""
    return Path(__file__).parent.parent.parent / "templates" / "project"


@pytest.fixture
def tmp_project_path(tmp_path):
    """Create a temporary directory for the project."""
    project_path = tmp_path / "test_project"
    yield project_path
    # Cleanup after test
    if project_path.exists():
        shutil.rmtree(project_path)


def test_bake_project(template_path, tmp_project_path):
    """Test basic project generation."""
    # Run copier copy
    worker = Worker(
        src_path=str(template_path),
        dst_path=str(tmp_project_path),
        data={"project_name": "test_project"}
    )
    worker.run_copy()

    # Verify the project was created
    assert tmp_project_path.exists()
    assert tmp_project_path.is_dir()
    assert (tmp_project_path / "pyproject.toml").exists()


def test_bake_then_run_project_tests(template_path, tmp_project_path):
    """Test project generation and running tests."""
    # Run copier copy
    worker = Worker(
        src_path=str(template_path),
        dst_path=str(tmp_project_path),
        data={"project_name": "test_project"}
    )
    worker.run_copy()

    # Copy required tools and libs
    tools_path = template_path.parent.parent / "tools"
    libs_path = template_path.parent.parent / "libs"
    shutil.copytree(tools_path, tmp_project_path.parent / "tools")
    shutil.copytree(libs_path, tmp_project_path.parent / "libs")

    # Run tests
    exit_code = os.system(f"cd {tmp_project_path} && make test")
    assert exit_code == 0, "Error running: make test in new copier project"


def test_project_nosql(template_path, tmp_project_path):
    """Test project generation with NoSQL database."""
    # Run copier copy
    worker = Worker(
        src_path=str(template_path),
        dst_path=str(tmp_project_path),
        data={
            "project_name": "test_project",
            "use_db": "y",
            "use_db_logic": "nosql"
        }
    )
    worker.run_copy()

    # Copy required tools and libs
    tools_path = template_path.parent.parent / "tools"
    libs_path = template_path.parent.parent / "libs"
    shutil.copytree(tools_path, tmp_project_path.parent / "tools")
    shutil.copytree(libs_path, tmp_project_path.parent / "libs")

    # Run tests
    exit_code = os.system(f"cd {tmp_project_path} && make test")
    assert exit_code == 0, "Error running: make test in new copier project"


def test_project_no_db(template_path, tmp_project_path):
    """Test project generation without database."""
    # Run copier copy
    worker = Worker(
        src_path=str(template_path),
        dst_path=str(tmp_project_path),
        data={
            "project_name": "test_project",
            "use_db": "n"
        }
    )
    worker.run_copy()

    # Copy required tools and libs
    tools_path = template_path.parent.parent / "tools"
    libs_path = template_path.parent.parent / "libs"
    shutil.copytree(tools_path, tmp_project_path.parent / "tools")
    shutil.copytree(libs_path, tmp_project_path.parent / "libs")

    # Run tests
    exit_code = os.system(f"cd {tmp_project_path} && make test")
    assert exit_code == 0, "Error running: make test in new copier project"


def test_project_no_api(template_path, tmp_project_path):
    """Test project generation without API."""
    # Run copier copy
    worker = Worker(
        src_path=str(template_path),
        dst_path=str(tmp_project_path),
        data={
            "project_name": "test_project",
            "use_api": "n"
        }
    )
    worker.run_copy()

    # Verify API files are not present
    api_path = tmp_project_path / "src" / "app" / "interactor" / "api"
    assert not api_path.exists(), "API directory should not exist when use_api is 'n'" 