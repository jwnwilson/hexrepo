#! /bin/bash

rm -rf dist

export UV_PUBLISH_URL="${HEXREPO_LIB_REPO_URL}"
export UV_PUBLISH_USERNAME=aws
export UV_PUBLISH_PASSWORD="${HEXREPO_LIB_REPO_PASSWORD}"

uv build
uv publish