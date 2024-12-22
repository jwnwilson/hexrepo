import os


def test_bake_library(cookies, update_path_libs, monkey_patch_cookiecutter_hooks):
    """Test for 'cookiecutter-template'."""
    result = cookies.bake(template="../../templates/library", extra_context={"project_name": "test_library"})

    assert result.exit_code == 0
    assert result.exception is None

    assert result.project_path.name == "test_library"
    assert result.project_path.is_dir()


def test_bake_then_run_libs_tests(cookies, update_path_libs, monkey_patch_cookiecutter_hooks):
    """Test for 'cookiecutter-template'."""
    result = cookies.bake(template="../../templates/library", extra_context={"project_name": "test_library"})

    assert result.exit_code == 0
    assert result.exception is None

    os.system(f"cp -r ../../tools {result.project_path.parent.parent.parent}")
    exit_code:int = os.system(f"cd {result.project_path} && make test")
    assert exit_code == 0, "Error running: make test in new cookiecutter library"
    