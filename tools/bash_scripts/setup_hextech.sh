#! /bin/bash

SCRIPT_DIR=$(dirname "$(realpath $0)")
ROOT_DIR=$(dirname $(dirname $SCRIPT_DIR))

if ! [ -x "$(command -v hextech)" ]; then
    echo "Installing Hextech cli..."
    uv tool install -e  ./tools/hextech
else
    # Hextech is installed
    exit 0
fi
