from typing import TYPE_CHECKING

import jinja2

from hextech.domain.project import find_repo_root

if TYPE_CHECKING:
    from hextech.domain.config import HexrepoConfig


def generate_libs_makefile(config: "HexrepoConfig"):
    project_root: str = find_repo_root()
    environment = jinja2.Environment(
        trim_blocks=True,
        lstrip_blocks=True,
    )
    with open(f"{project_root}/templates/library/Makefile.template") as f:
        template = environment.from_string(f.read())
    libs_makefile_content: str = template.render(
        cloud_provider=config.cloud_provider,
    )
    with open(f"{project_root}libs/Makefile", "w") as f:
        f.write(libs_makefile_content)


def generate_project_makefile(config: "HexrepoConfig"):
    project_root: str = find_repo_root()
    environment = jinja2.Environment(
        trim_blocks=True,
        lstrip_blocks=True,
    )
    with open(f"{project_root}/templates/project/cookiecutter.pre.json.template") as f:
        template = environment.from_string(f.read())
    project_cookiecutter_content: str = template.render(
        cloud_provider=config.cloud_provider,
        domain=config.domain,
    )
    with open(f"{project_root}/templates/project/cookiecutter.pre.json", "w") as f:
        f.write(project_cookiecutter_content)
