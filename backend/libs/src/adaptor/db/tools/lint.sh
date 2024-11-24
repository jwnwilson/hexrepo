#!/usr/bin bash

set -e
VENV=.venv

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -c|--check) check=true; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
done


APP_FOLDER="monorepo_db tests"

if [[ -z "${GITHUB_ACTIONS}" ]]; then
    echo "Running locally, activating venv."
    . ${VENV_DIR}/bin/activate
else
    echo "Running on github skipping venv creation."
    . $(poetry env info --path)/bin/activate
fi

if [[ -z "${check}" ]]; then
    black ${APP_FOLDER} 
    isort ${APP_FOLDER} --profile black
else
    mypy ${APP_FOLDER}
    black --check ${APP_FOLDER}
    isort --check-only ${APP_FOLDER} --profile black
fi
