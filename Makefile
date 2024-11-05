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

create_project:
	@echo "Creating project..."
	poetry new $(PROJECT_NAME)

create_library:
	@echo "Creating library..."
	poetry new $(LIBRARY_NAME)	
