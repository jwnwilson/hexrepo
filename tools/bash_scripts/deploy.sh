#! /bin/bash

set -e

# check if DOCKER_TAG_CONTAINER is set
if [ -z "$DOCKER_TAG_CONTAINER" ] && [ -z "$DOCKER_TAG_SERVERLESS" ]; then
    echo "DOCKER_TAG_CONTAINER or DOCKER_TAG_SERVERLESS env var is not set"
    exit 1
fi

# check if TARGETS is seta
if [ -z "$TARGETS" ]; then
    echo "TARGETS env var is not set"
    exit 1
fi

if [ "${DOCKER_TAG_CONTAINER}" != "" ]; then
    make tf_apply_no_input TF_VAR_docker_tag_container=${DOCKER_TAG_CONTAINER} TARGETS="${TARGETS}"
else
    make tf_apply_no_input TF_VAR_docker_tag_serverless=${DOCKER_TAG_SERVERLESS} TARGETS="${TARGETS}"
fi
