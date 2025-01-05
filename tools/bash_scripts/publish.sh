#! /bin/bash

rm -rf dist
. ${VENV_DIR}/bin/activate
uvx publish \
--username=${HEXREPO_LIB_REPO_USERNAME} \
--password=${HEXREPO_LIB_REPO_PASSWORD} \
--publish-url=${HEXREPO_LIB_REPO_URL}