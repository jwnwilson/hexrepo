#! /bin/bash

rm -rf dist
. ${VENV_DIR}/bin/activate
uvx publish \
--username=${MONOREPO_LIB_REPO_PASSWORD} \
--password=${MONOREPO_LIB_REPO_PASSWORD} \
--publish-url=${MONOREPO_LIB_REPO_URL}