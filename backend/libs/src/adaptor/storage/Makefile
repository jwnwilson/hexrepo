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
	bash ./tools/lint.sh

lint_check: venv
	bash ./tools/lint.sh --check

clean:
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

publish: venv
	@echo "Publishing package..."
	@./tools/publish.sh

