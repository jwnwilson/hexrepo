.PHONY: venv test lint
.DEFAULT_GOAL = help
.EXPORT_ALL_VARIABLES:

VENV := .venv
MKFILE_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
VENV_DIR = $(MKFILE_DIR)$(VENV)

# Setup commands
venv:
	@echo "Checking if venv is setup..."
	@./tools/setup_env.sh

test: venv
	@echo "Running tests..."
	. $(VENV_DIR)/bin/activate; \
	pytest

lint: venv
	@echo "Linting"
	. $(VENV_DIR)/bin/activate; \
	black python/
	flake8 python/

clean:
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

publish: venv
	@echo "Publishing package..."
	@./tools/publish.sh

