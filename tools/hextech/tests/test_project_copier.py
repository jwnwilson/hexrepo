import os
import shutil
from pathlib import Path
import pytest
from copier import run_copy

from .utils import copy_project_dependencies


@pytest.fixture
def template_path():
    """Return the path to the template directory."""
    return Path(__file__).parent.parent.parent.parent / "templates" / "project"


@pytest.fixture
def tmp_project_path(tmp_path):
    """Create a temporary directory for the project."""
    project_path = tmp_path / "test_project"
    yield project_path
    # Cleanup after test
    if project_path.exists():
        shutil.rmtree(project_path)


def test_copy_project(template_path, tmp_project_path):
    """Test basic project generation."""
    # Run copier copy
    result = run_copy(
        src_path=str(template_path),
        dst_path=str(tmp_project_path),
        data={
            "project_name": "test_project",
            "description": "Test project",
            "full_name": "Test User",
        },
        defaults=True
    )

    # Verify the project was created
    assert tmp_project_path.exists()
    assert tmp_project_path.is_dir()
    assert (tmp_project_path / "pyproject.toml").exists()


def test_copy_then_run_project_tests(template_path, tmp_project_path):
    """Test project generation and running tests."""
    # Run copier copy
    run_copy(
        src_path=str(template_path),
        dst_path=str(tmp_project_path),
        data={
            "project_name": "test_project",
            "description": "Test project",
            "full_name": "Test User",
        },
        defaults=True
    )

    # Copy required tools and libs efficiently
    copy_project_dependencies(template_path.parent.parent, tmp_project_path)

    # Run tests
    exit_code = os.system(f"cd {tmp_project_path} && make test")
    assert exit_code == 0, "Error running: make test didn't run successfully in new copier project"


# Need to add dynamo db create table logic to template to enable this test
# def test_project_nosql(template_path, tmp_project_path):
#     """Test project generation with NoSQL database."""
#     # Run copier copy
#     run_copy(
#         src_path=str(template_path),
#         dst_path=str(tmp_project_path),
#         data={
#             "project_name": "test_project",
#             "description": "Test project",
#             "full_name": "Test User",
#             "use_db": "y",
#             "use_db_logic": "nosql"
#         },
#         defaults=True
#     )

#     # Copy required tools and libs efficiently
#     copy_project_dependencies(template_path.parent.parent, tmp_project_path)

#     # Run tests
#     exit_code = os.system(f"cd {tmp_project_path} && make test")
#     assert exit_code == 0, "Error running: make test in new copier project"


# def test_project_no_db(template_path, tmp_project_path):
#     """Test project generation without database."""
#     # Run copier copy
#     run_copy(
#         src_path=str(template_path),
#         dst_path=str(tmp_project_path),
#         data={
#             "project_name": "test_project",
#             "description": "Test project",
#             "full_name": "Test User",
#             "use_db": "n"
#         },
#         defaults=True
#     )

#     # Copy required tools and libs efficiently
#     copy_project_dependencies(template_path.parent.parent, tmp_project_path)

#     # Run tests
#     exit_code = os.system(f"cd {tmp_project_path} && make test")
#     assert exit_code == 0, "Error running: make test in new copier project"


def test_project_no_api(template_path, tmp_project_path):
    """Test project generation without API."""
    # Run copier copy
    run_copy(
        src_path=str(template_path),
        dst_path=str(tmp_project_path),
        data={
            "project_name": "test_project",
            "description": "Test project",
            "full_name": "Test User",
            "use_api": "n"
        },
        defaults=True
    )

    # Verify API files are not present
    api_path = tmp_project_path / "src" / "app" / "interactor" / "api"
    assert not api_path.exists(), "API directory should not exist when use_api is 'n'" 