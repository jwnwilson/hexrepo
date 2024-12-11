#! /bin/bash
VENV=.venv
CURRENT_DIR=.

if [ -d "./.venv" ]; then
    echo "Virtual environment already exists, skipping venv creation."
    exit 0
fi

echo "Setting up virtual environment in directory: {PWD}"

python3.12 -m venv ${VENV}; \
source ${CURRENT_DIR}/${VENV}/bin/activate && \
export SYSTEM_VERSION_COMPAT=1 && \
pip install poetry && \
poetry lock && \
poetry install --with dev