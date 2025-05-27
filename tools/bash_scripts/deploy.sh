#! /bin/bash

set -e

# check if IMAGE is set
if [ -z "$IMAGE" ]; then
    echo "IMAGE env var is not set"
    exit 1
fi
# check if DOCKER_TAG is set
if [ -z "$DOCKER_TAG" ]; then
    echo "DOCKER_TAG env var is not set"
    exit 1
fi
# check if TARGETS is set
if [ -z "$TARGETS" ]; then
    echo "TARGETS env var is not set"
    exit 1
fi

if [ "${NO_INPUT}" == "True" ]; then
    make tf_apply_no_input TF_VAR_docker_tag=${DOCKER_TAG} TARGETS=${TARGETS}
else
    make tf_apply TF_VAR_docker_tag=${DOCKER_TAG} TARGETS=${TARGETS}
fi
