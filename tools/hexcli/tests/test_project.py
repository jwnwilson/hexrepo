def test_bake_custom_project(cookies, update_path_project, monkey_patch_cookiecutter_hooks):
    """Test for 'cookiecutter-template'."""
    result = cookies.bake(template="../../templates/project", extra_context={"testing": "True"})

    assert result.exit_code == 0
    assert result.exception is None

    assert result.project_path.name == "Name of the project"
    assert result.project_path.is_dir()