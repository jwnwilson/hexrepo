#! /bin/bash

if [[ -z "${GITHUB_ACTIONS}" ]]; then
    echo "Running locally, activating venv."
    . ${VENV_DIR}/bin/activate
else
    echo "Running on github skipping venv activation."
    . $(poetry env info --path)/bin/activate
fi

pytest