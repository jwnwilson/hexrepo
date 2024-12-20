def test_bake_library(cookies, update_path_libs, monkey_patch_cookiecutter_hooks):
    """Test for 'cookiecutter-template'."""
    result = cookies.bake(template="../../templates/library", extra_context={"testing": "True"})

    assert result.exit_code == 0
    assert result.exception is None

    assert result.project_path.name == "Name of the project"
    assert result.project_path.is_dir()