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


@pytest.fixture
def monkey_patch_cookiecutter_hooks():
    """Cookie cutter doesn't provide a good way to interact with hooks
    during testing, as a workaround monkey patching the run_script function.

    The moneky patch will pass test env vars to the hook scripts.
    """
    def new_run_script(script_path, cwd='.'):
        """Execute a script from a working directory.

        :param script_path: Absolute path to the script to run.
        :param cwd: The directory to run the script from.
        """
        from cookiecutter import utils
        from cookiecutter.exceptions import FailedHookException
        from cookiecutter.hooks import EXIT_SUCCESS
        import errno

        
        run_thru_shell = sys.platform.startswith('win')
        if script_path.endswith('.py'):
            script_command = [sys.executable, script_path]
        else:
            script_command = [script_path]

        utils.make_executable(script_path)

        try:
            # setting env variable for testing
            proc = subprocess.Popen(script_command, shell=run_thru_shell, cwd=cwd, env={"TESTING": "True"})  # nosec
            exit_status = proc.wait()
            if exit_status != EXIT_SUCCESS:
                raise FailedHookException(
                    f'Hook script failed (exit status: {exit_status})'
                )
        except OSError as err:
            if err.errno == errno.ENOEXEC:
                raise FailedHookException(
                    'Hook script failed, might be an empty file or missing a shebang'
                ) from err
            raise FailedHookException(f'Hook script failed (error: {err})') from err


    with mock.patch('cookiecutter.hooks.run_script', new_run_script):
        yield
