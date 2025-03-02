.PHONY: hextech test lint
.DEFAULT_GOAL = help
.EXPORT_ALL_VARIABLES:

VENV=.venv
VENV_DIR = $(MKFILE_DIR)$(VENV)
LIBRARY:=${LIBRARY}
PROJECT:=${PROJECT}
ENV:=${ENV}

# Setup commands
hextech:
	@./tools/bash_scripts/setup_hextech.sh

setup: hextech
	@echo "Setting up hexrepo..."
	hextech setup

shared_infra_plan: hextech
	@echo "Planning shared infra..."
	hextech shared-infra-plan

shared_infra_apply: hextech
	@echo "Applying shared infra..."
	hextech shared-infra-apply

env_infra_plan: hextech
	@echo "Planning env infra..."
	hextech env-infra-plan $(ENV)

env_infra_apply: hextech
	@echo "Applying env infra..."
	hextech env-infra-apply $(ENV)

create_project: hextech
	@echo "Creating project..."
	hextech create-project

create_library: hextech
	@echo "Creating library..."
	hextech create-library

add_library: hextech
	@echo "Adding library to project..."
	hextech add-library

test_projects: hextech
	@echo "Testing projects..."
	hextech test-projects

test_libs: hextech
	@echo "Testing libraries..."
	hextech test-libs --libraries=$(LIBRARY)

check_library_modified: hextech
	@echo "Checking library modified..."
	hextech check-library-modified $(LIBRARY)

check_project_modified: hextech
	@echo "Checking project modified..."
	hextech check-project-modified $(PROJECT)

check_library_bump: hextech
	@echo "Checking library bump..."
	hextech check-library-bump $(LIBRARY)

bump_library_version: hextech
	@echo "Bumping version..."
	hextech bump-librariy-version

test_tools: hextech
	@echo "Testing tools..."
	hextech test-tools

lint: hextech
	@echo "Linting hextech repo..."
	hextech lint

deploy_projects: hextech
	@echo "Deploying projects..."
	hextech deploy-projects $(ENV) --no-input

deploy_projects_check_modified: hextech
	@echo "Deploying projects..."
	hextech deploy-projects $(ENV) --check-modified --no-input

deploy_libs: hextech
	@echo "Deploying libraries..."
	hextech deploy-libs --no-input

deploy_libs_check_modified: hextech
	@echo "Deploying libraries..."
	hextech deploy-libs --check-modified --no-input

stop_infra: hextech
	@echo "Stopping infra..."
	hextech stop-infra

start_infra: hextech
	@echo "Starting infra..."
	hextech start-infra

destroy_infra: hextech
	@echo "Destroying infra..."
	hextech destroy

bastion: hextech
	@echo "Starting bastion..."
	hextech bastion

migrate_db: hextech
	@echo "Starting bastion..."
	hextech migrate-db ${ENV} ${PROJECT}

create_user: hextech
	@echo "Starting bastion..."
	hextech create-user ${ENV} ${PROJECT}

create_permissions: hextech
	@echo "Starting bastion..."
	hextech create-permissions ${ENV} ${PROJECT}

update_projects_from_template: hextech
	@echo "Updating projects from template..."
	hextech update-projects-from-template
