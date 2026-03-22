.PHONY: venv test lint
.DEFAULT_GOAL = help
.EXPORT_ALL_VARIABLES:

VENV := .venv
MKFILE_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
VENV_DIR = $(MKFILE_DIR)$(VENV)

# Setup commands
venv:
	@../../tools/bash_scripts/setup_env.sh

lint:
 	@TARGET_DIRS="src" bash ../../tools/bash_scripts/lint.sh 

lint_check: venv
	@TARGET_DIRS="src" bash ../../tools/bash_scripts/lint.sh --check

clean:
	@find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

notebook:
	docker compose up

test: venv
	@echo "Running unit tests"
	uv run pytest

