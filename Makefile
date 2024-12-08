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
	@./tools/setup_env.sh

setup: venv
	@echo "Setting up monorep..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py setup

shared_infra_plan: venv
	@echo "Planning shared infra..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py shared-infra-plan

shared_infra_apply: venv
	@echo "Applying shared infra..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py shared-infra-apply

env_infra_plan: venv
	@echo "Planning env infra..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py env-infra-plan $(ENV)

env_infra_apply: venv
	@echo "Applying env infra..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py env-infra-apply $(ENV)

create_project: venv
	@echo "Creating project..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py create-project

create_library: venv
	@echo "Creating library..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py create-library

add_library: venv
	@echo "Adding library to project..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py add_library

test_projects: venv
	@echo "Testing projects..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py test-projects

test_libs: venv
	@echo "Testing libraries..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py test-libs --libraries=$(LIBRARY)

lint_projects: venv
	@echo "Linting projects..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py lint_projects

lint_libs: venv
	@echo "Linting libraries..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py lint_libs

deploy_projects: venv
	@echo "Deploying projects..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py deploy-projects --projects=$(PROJECT) --check-modified --no-input

deploy_libs: venv
	@echo "Deploying libraries..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py deploy-libs --libraries=$(LIBRARY) --check-modified --no-input

bastion: venv
	@echo "Creating bastion..."
	@. $(VENV_DIR)/bin/activate; \
	# python cli.py bastion --env=$(ENV)
	aws ssm start-session \
	--target i-0ebb96e385446d037 \
	--document-name AWS-StartPortForwardingSession \
    --parameters '{"portNumber":["5432"],"localPortNumber":["5432"], "host":["example-db-default.clfqqiusnlbr.eu-west-1.rds.amazonaws.com"]}'

migrate_db: venv
	@echo "Migrating database..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py migrate-db

stop_infra: venv
	@echo "Stopping infra..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py stop-infra

start_infra: venv
	@echo "Starting infra..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py start-infra
