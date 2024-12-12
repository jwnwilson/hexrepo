.PHONY: venv test lint
.DEFAULT_GOAL = help
.EXPORT_ALL_VARIABLES:

VENV=.venv
VENV_DIR = $(MKFILE_DIR)$(VENV)
LIBRARY:=${LIBRARY}
PROJECT:=${PROJECT}
ENV:=${ENV}

# Setup commands
venv:
	@echo "Checking if venv is setup..."
	@./tools/bash_scripts/setup_root_env.sh

setup: venv
	@echo "Setting up monorep..."
	@. $(VENV_DIR)/bin/activate && \
	hexcli setup

shared_infra_plan: venv
	@echo "Planning shared infra..."
	@. $(VENV_DIR)/bin/activate && \
	hexcli shared-infra-plan

shared_infra_apply: venv
	@echo "Applying shared infra..."
	@. $(VENV_DIR)/bin/activate && \
	hexcli shared-infra-apply

env_infra_plan: venv
	@echo "Planning env infra..."
	@. $(VENV_DIR)/bin/activate && \
	hexcli env-infra-plan $(ENV)

env_infra_apply: venv
	@echo "Applying env infra..."
	@. $(VENV_DIR)/bin/activate && \
	hexcli env-infra-apply $(ENV)

create_project: venv
	@echo "Creating project..."
	@. $(VENV_DIR)/bin/activate && \
	hexcli create-project

create_library: venv
	@echo "Creating library..."
	@. $(VENV_DIR)/bin/activate && \
	hexcli create-library

add_library: venv
	@echo "Adding library to project..."
	@. $(VENV_DIR)/bin/activate && \
	hexcli add_library

test_projects: venv
	@echo "Testing projects..."
	@. $(VENV_DIR)/bin/activate && \
	hexcli test-projects

test_libs: venv
	@echo "Testing libraries..."
	@. $(VENV_DIR)/bin/activate && \
	hexcli test-libs --libraries=$(LIBRARY)

lint_projects: venv
	@echo "Linting projects..."
	@. $(VENV_DIR)/bin/activate && \
	hexcli lint_projects

lint_libs: venv
	@echo "Linting libraries..."
	@. $(VENV_DIR)/bin/activate && \
	hexcli lint_libs

deploy_projects: venv
	@echo "Deploying projects..."
	@. $(VENV_DIR)/bin/activate && \
	hexcli deploy-projects $(ENV) --projects=$(PROJECT) --check-modified --no-input

deploy_libs: venv
	@echo "Deploying libraries..."
	@. $(VENV_DIR)/bin/activate && \
	hexcli deploy-libs --libraries=$(LIBRARY) --check-modified --no-input

stop_infra: venv
	@echo "Stopping infra..."
	@. $(VENV_DIR)/bin/activate && \
	hexcli stop-infra

start_infra: venv
	@echo "Starting infra..."
	@. $(VENV_DIR)/bin/activate && \
	hexcli start-infra
