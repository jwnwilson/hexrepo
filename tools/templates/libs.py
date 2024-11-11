import jinja2

def generate_libs_makefile(cloud_provider: str):
    environment = jinja2.Environment(
        trim_blocks=True,
        lstrip_blocks=True,
    )
    with open("backend/templates/library/Makefile.template") as f:
        template = environment.from_string(f.read())
    libs_makefile_content: str = template.render(
        cloud_provider=cloud_provider
    )
    with open("backend/libs/Makefile", "w") as f:
        f.write(libs_makefile_content)
