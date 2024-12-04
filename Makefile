.PHONY: venv test lint
.DEFAULT_GOAL = help
.EXPORT_ALL_VARIABLES:

VENV=.venv
VENV_DIR = $(MKFILE_DIR)$(VENV)
LIBRARY:=${LIBRARY}

# Setup commands
venv:
	@echo "Checking if venv is setup..."
	@./tools/setup_env.sh

setup: venv
	@echo "Setting up monorep..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py setup

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
	python cli.py deploy-projects

deploy_libs: venv
	@echo "Deploying libraries..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py deploy-libs --libraries=$(LIBRARY) --check-modified --no-input

migrate_db: venv
	@echo "Migrating database..."
	@. $(VENV_DIR)/bin/activate; \
	python cli.py migrate_db
