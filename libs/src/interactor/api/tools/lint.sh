#!/usr/bin bash

set -e
VENV=.venv

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -c|--check) check=true; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
done


APP_FOLDER="monorepo_api tests"

echo "Activating venv."
. ${VENV_DIR}/bin/activate

if [[ -z "${check}" ]]; then
    black ${APP_FOLDER} 
    isort ${APP_FOLDER} --profile black
else
    mypy ${APP_FOLDER}
    black --check ${APP_FOLDER}
    isort --check-only ${APP_FOLDER} --profile black
fi
