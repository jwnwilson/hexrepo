.PHONY: venv test lint
.DEFAULT_GOAL = help

VENV=.venv
VENV_DIR = $(MKFILE_DIR)$(VENV)

# Setup commands
venv:
	@echo "Checking if venv is setup..."
	@./tools/setup_env.sh

setup: venv
	@echo "Setting up monorep..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py setup

create_be_project: venv
	@echo "Creating project..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py create-be-project

create_be_library: venv
	@echo "Creating library..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py create-be-library

add_be_library: venv
	@echo "Adding library to project..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py add_be_library

test_be_projects:
	@echo "Testing projects..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py test-be-projects

test_be_libs:
	@echo "Testing libraries..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py test-be-libs

lint_be_projects:
	@echo "Linting projects..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py lint_be_projects

lint_be_libs:
	@echo "Linting libraries..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py lint_be_libs

deploy_be_projects:
	@echo "Deploying projects..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py deploy_be_projects

deploy_be_libs:
	@echo "Deploying libraries..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py deploy_be_libs

migrate_db:
	@echo "Migrating database..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py migrate_db
