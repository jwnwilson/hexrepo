#!/usr/bin/env python
import os
import shutil
import yaml
import logging

logger = logging.getLogger(__name__)

MANIFEST = "manifest.yml"


def delete_resources_for_disabled_features():
    with open(MANIFEST) as manifest_file:
        manifest = yaml.load(manifest_file)
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
    libraries = '{{ cookiecutter.libraries }}'.split(',')
    for lib in libraries:
        logger.info( f"installing library: {lib}" )
        os.system(f"poetry install -E ../../libs/src/{lib}")


if __name__ == "__main__":
    delete_resources_for_disabled_features()
    install_libraries()