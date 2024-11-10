#!/usr/bin/env python
import os
import shutil
import yaml
import logging

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
    print("Skipping library install until library repo is available")
    return
    CLOUD_PROVIDER = "{{ cookiecutter.cloud_provider }}"
    use_db = '{{ cookiecutter.use_db }}'
    use_storage = '{{ cookiecutter.use_storage }}'
    if use_db:
        logger.info( f"installing library: db" )
        os.system(f"poetry add monorepo_db -G prod")
    if use_storage:
        logger.info( f"installing library: storage" )
        os.system(f"poetry add monorepo_storage -G prod")


if __name__ == "__main__":
    delete_resources_for_disabled_features()
    install_libraries()