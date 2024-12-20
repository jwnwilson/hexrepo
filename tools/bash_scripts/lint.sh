#!/usr/bin bash

set -e
VENV=.venv

if [[ -z "${TARGET_DIRS}" ]]; then
    echo "TARGET_DIRS is not set. Exiting."
    exit 1
fi

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -c|--check) check=true; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
done


. ${VENV}/bin/activate

if [[ -z "${check}" ]]; then
    black ${TARGET_DIRS} 
    isort ${TARGET_DIRS} --profile black
else
    mypy ${TARGET_DIRS}
    black --check ${TARGET_DIRS}
    isort --check-only ${TARGET_DIRS} --profile black
fi
