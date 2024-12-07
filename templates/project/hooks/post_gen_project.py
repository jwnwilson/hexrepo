#!/usr/bin/env python
import os
import shutil
import yaml
import logging

from tools.logic.commands import run_system_command

logger = logging.getLogger(__name__)

MANIFEST = "manifest.yml"


def delete_resources_for_disabled_features():
    with open(MANIFEST) as manifest_file:
        manifest = yaml.load(manifest_file, Loader=yaml.Loader)
        for feature in manifest['features']:
            if not feature['enabled']:
                logger.info("removing resources for disabled feature {}...".format(feature['name']))
                for resource in feature['resources']:
                    delete_resource(resource)
    logger.info( "cleanup complete, removing manifest..." )
    delete_resource(MANIFEST)


def delete_resource(resource):
    if os.path.isfile(resource):
        logger.info( "removing file: {}".format(resource) )
        os.remove(resource)
    elif os.path.isdir(resource):
        logger.info( "removing directory: {}".format(resource) )
        shutil.rmtree(resource)


def install_libraries():
    # Deprecated, using local editable libraries over deployed libraries
    CLOUD_PROVIDER = "{{ cookiecutter.cloud_provider }}"
    use_db = '{{ cookiecutter.use_db }}'
    use_storage = '{{ cookiecutter.use_storage }}'
    use_api = '{{ cookiecutter.use_api }}'

    run_system_command("make venv")
    run_system_command("source ./.venv/bin/activate && poetry config http-basic.monorepo $MONOREPO_LIB_REPO_USERNAME $MONOREPO_LIB_REPO_PASSWORD")
    run_system_command("source ./.venv/bin/activate && poetry source add --priority=supplemental monorepo ${MONOREPO_LIB_REPO_URL}simple")
    
    if use_db:
        logger.info("installing library: db" )
        run_system_command("source ./.venv/bin/activate && poetry add --source monorepo monorepo-db -G prod")
    if use_storage:
        logger.info("installing library: storage" )
        run_system_command("source ./.venv/bin/activate && poetry add --source monorepo monorepo-storage -G prod")
    if use_api:
        logger.info("installing library: api" )
        run_system_command("source ./.venv/bin/activate && poetry add --source monorepo monorepo-api -G prod")

    print("dynamically add pip install -e commands to develop libs script")


if __name__ == "__main__":
    delete_resources_for_disabled_features()
    # install_libraries()