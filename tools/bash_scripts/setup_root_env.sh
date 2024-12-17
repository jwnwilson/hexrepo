#! /bin/bash
VENV=.venv
SCRIPT_DIR=$(dirname "$(realpath $0)")
ROOT_DIR=$(dirname $(dirname $SCRIPT_DIR))

if [ -d "${ROOT_DIR}/.venv" ]; then
    echo "Cli virtual environment already exists, skipping venv creation."
    exit 0
else
    cd $ROOT_DIR
    echo "Setting up Cli virtual environment in directory: ${PWD}"
    python3.12 -m venv ${VENV}
    source ${ROOT_DIR}/${VENV}/bin/activate && \
    export SYSTEM_VERSION_COMPAT=1 && \
    pip install poetry  && \
    poetry install
fi
