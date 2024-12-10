#! /bin/bash

rm -rf dist
. ${VENV_DIR}/bin/activate; \
poetry config repositories.monorep ${MONOREPO_LIB_REPO_URL}
@poetry config http-basic.monorep ${MONOREPO_LIB_REPO_USERNAME} ${MONOREPO_LIB_REPO_PASSWORD}
poetry version patch
poetry publish --build --repository monorep