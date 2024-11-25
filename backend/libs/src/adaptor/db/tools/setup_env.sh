#! /bin/bash
VENV=.venv
SCRIPT_DIR=$(dirname "$(realpath $0)")
ROOT_DIR=$(dirname $SCRIPT_DIR)

if [ -d "./.venv" ]; then
    echo "Virtual environment already exists, skipping venv creation."
    exit 0
fi

if [[ -z "${GITHUB_ACTIONS}" ]]; then
    echo "Running locally, creating venv."
    cd $ROOT_DIR
    python3.12 -m venv ${VENV}; \
    source ${ROOT_DIR}/${VENV}/bin/activate && \
    export SYSTEM_VERSION_COMPAT=1 && \
    pip install poetry  && \
    poetry install --with dev
else
    echo "Running on github skipping venv creation."
    . $(poetry env info --path)/bin/activate
    echo `which python`
    poetry install --with dev
fi
