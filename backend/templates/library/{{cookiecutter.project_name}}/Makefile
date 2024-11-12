.PHONY: venv test lint
.DEFAULT_GOAL = help

VENV := .venv
MKFILE_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
VENV_DIR = $(MKFILE_DIR)$(VENV)

# Setup commands
venv:
	@echo "Creating virtual environment..."
	python3.12 -m venv $(VENV); \
	source $(VENV_DIR)/bin/activate && \
	export SYSTEM_VERSION_COMPAT=1 && \
	pip install poetry && \
	poetry install

test:
	@echo "Running tests..."
	. $(VENV_DIR)/bin/activate; \
	pytest

lint:
	@echo "Linting"
	. $(VENV_DIR)/bin/activate; \
	black python/
	flake8 python/

clean:
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

publish:
	@echo "Publishing package..."
	. $(VENV_DIR)/bin/activate; \
	poetry config repositories.monorep $(MONOREPO_LIB_REPO_URL)
	poetry config http-basic.monorep $(MONOREPO_LIB_REPO_USERNAME) $(MONOREPO_LIB_REPO_PASSWORD)
	poetry publish --build --repository monorep

