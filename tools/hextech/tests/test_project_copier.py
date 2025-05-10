import os
import shutil
from pathlib import Path
import pytest
from copier import run_copy
from copier.main import Worker


def copy_project_dependencies(src_path: Path, dst_path: Path, components: list[str] = None, exclude_dirs: list[str] = None) -> None:
    """Copy project dependencies (tools and libs) to test folder so relative imports work during tests
    
    Args:
        src_path: Source path containing tools and libs
        dst_path: Destination path to copy to
        components: List of components to copy (e.g. ['tools', 'libs']). Defaults to ['tools', 'libs']
        exclude_dirs: List of directory names to exclude (e.g. ['.venv', '__pycache__'])
    """
    components = components or ['tools', 'libs']
    exclude_dirs = exclude_dirs or ['.venv', '__pycache__', '.git', '.pytest_cache', '.coverage', 'htmlcov']
    
    def should_copy(path: Path) -> bool:
        return not any(excluded in path.parts for excluded in exclude_dirs)
    
    def copy_component(component: str) -> None:
        src = src_path / component
        dst = dst_path.parent.parent / component
        if src.exists():
            for item in src.rglob("*"):
                if should_copy(item):
                    rel_path = item.relative_to(src)
                    dst_item = dst / rel_path
                    if item.is_file():
                        dst_item.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dst_item)
    
    for component in components:
        copy_component(component)


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


def test_bake_project(template_path, tmp_project_path):
    """Test basic project generation."""
    # Run copier copy
    worker = Worker(
        src_path=str(template_path),
        dst_path=str(tmp_project_path),
        data={
            "project_name": "test_project",
            "description": "Test project",
            "full_name": "Test User",
        },
        defaults=True
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
        data={
            "project_name": "test_project",
            "description": "Test project",
            "full_name": "Test User",
        },
        defaults=True
    )
    worker.run_copy()

    # Copy required tools and libs efficiently
    copy_project_dependencies(template_path.parent.parent, tmp_project_path)

    # Run tests
    breakpoint()
    exit_code = os.system(f"cd {tmp_project_path} && make test")
    assert exit_code == 0, "Error running: make test didn't run successfully in new copier project"


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

    # Copy required tools and libs efficiently
    copy_project_dependencies(template_path.parent.parent, tmp_project_path)

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

    # Copy required tools and libs efficiently
    copy_project_dependencies(template_path.parent.parent, tmp_project_path)

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