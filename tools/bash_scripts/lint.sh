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


if [[ -z "${check}" ]]; then
    uv run ruff check --select I --fix ${TARGET_DIRS}
    uv run ruff check --fix ${TARGET_DIRS}
    uv run ruff format ${TARGET_DIRS}
else
    uv run ruff check --select I ${TARGET_DIRS}
    uv run ruff check ${TARGET_DIRS}
    mypy ${TARGET_DIRS}
fi
