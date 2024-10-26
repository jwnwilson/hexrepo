#!/usr/bin/env bash

set -e
set -x

#!/bin/bash

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -c|--check) check=true; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
done

APP_FOLDER=app

if [[ -z "${check}" ]]; then
    black ${APP_FOLDER} 
    isort ${APP_FOLDER} --profile black
else
    mypy ${APP_FOLDER}
    black --check ${APP_FOLDER}
    isort --check-only ${APP_FOLDER} --profile black
fi
