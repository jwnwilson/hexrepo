from pathlib import Path
import shutil


def copy_project_dependencies(
        src_path: Path,
        dst_path: Path,
        components: list[str] = None,
        exclude_dirs: list[str] = None,
        lib: bool = False) -> None:
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
        if lib:
            dst = dst_path.parent.parent / component
        else:
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
