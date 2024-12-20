import os


def test_bake_project(cookies, update_path_project, monkey_patch_cookiecutter_hooks):
    """Test for 'cookiecutter-template'."""
    result = cookies.bake(template="../../templates/project", extra_context={"project_name": "test_project"})

    assert result.exit_code == 0
    assert result.exception is None

    assert result.project_path.name == "test_project"
    assert result.project_path.is_dir()


def test_bake_then_run_project_tests(cookies, update_path_project, monkey_patch_cookiecutter_hooks):
    """Test for 'cookiecutter-template'."""
    result = cookies.bake(template="../../templates/project", extra_context={"project_name": "test_project"})

    assert result.exit_code == 0
    assert result.exception is None

    os.system(f"cp -r ../../tools {result.project_path.parent.parent}")
    os.system(f"cp -r ../../libs {result.project_path.parent.parent}")
    exit_code:int = os.system(f"cd {result.project_path} && make test")
    assert exit_code == 0, "Error running: make test in new cookiecutter project"
    