#! /bin/bash
VENV=.venv
SCRIPT_DIR=$(dirname "$(realpath $0)")
ROOT_DIR=$(dirname $SCRIPT_DIR)

if [ -d "./.venv" ]; then
    echo "Virtual environment already exists, skipping venv creation."
    exit 0
fi

cd $ROOT_DIR
python3.12 -m venv ${VENV}; \
source ${ROOT_DIR}/${VENV}/bin/activate && \
export SYSTEM_VERSION_COMPAT=1 && \
pip install poetry --all-extras && \
poetry lock && \
poetry install