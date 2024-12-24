#! /bin/bash
VENV=.venv
CURRENT_DIR=.

if [ -d "./.venv" ]; then
    # Venv already exists, skip creation
    # echo "Virtual environment already exists, skipping venv creation."
    exit 0
fi

echo "Activating virtual environment in directory: ${PWD}"

python3.12 -m venv ${VENV}; \
source ${CURRENT_DIR}/${VENV}/bin/activate && \
uv sync --all-extras