.PHONY: venv test lint
.DEFAULT_GOAL = help

VENV := .venv
MKFILE_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
VENV_DIR = $(MKFILE_DIR)$(VENV)

# Setup commands
venv:
	@echo "Checking if venv is setup..."
	@./tools/setup_env.sh

test:
	@echo "Running tests..."
	. $(VENV_DIR)/bin/activate; \
	pytest

coverage:
	@echo "Running unit tests"	
	. $(VENV_DIR)/bin/activate; \
	pytest --cov-report html	

lint:
	bash ./tools/lint.sh

clean:
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

publish:
	@echo "Publishing package..."
	@./tools/publish.sh

