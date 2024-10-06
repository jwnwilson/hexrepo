.PHONY: venv_setup test lint

.DEFAULT_GOAL = help

help:
	@echo "---------------HELP-----------------"
	@echo "To setup the project type make setup"
	@echo "To test the project type make test"
	@echo "------------------------------------"
VENV := .venv
MKFILE_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
VENV_DIR = $(MKFILE_DIR)$(VENV)

local_run: db_upgrade local_server
build: check_for_sa_creds build_docker
test: db_test_stop db_test_start pytest db_test_stop

# Setup commands
venv_setup:
	@echo "Creating virtual environment..."
	python3.12 -m venv $(VENV); \
	source $(VENV_DIR)/bin/activate && \
	export SYSTEM_VERSION_COMPAT=1 && \
	pip install poetry && \
	gcloud auth login && \
	poetry self add keyrings.google-artifactregistry-auth && \
	poetry install
	@echo "Installing pre commit hook..."
	source $(VENV_DIR)/bin/activate && pre-commit install --install-hooks

build_docker:
	docker compose build 

# DB management
db_delete_data:
	docker compose run postgres_db bash -c "rm -rf /var/lib/postgresql/data/*"

db_upgrade:
	source $(VENV_DIR)/bin/activate && \
	docker compose run api bash -c "alembic upgrade head"

db_downgrade:
	docker compose run api bash -c "alembic downgrade -1"

db_create_migration:
	docker compose run api bash -c "alembic revision --autogenerate -m \"DB migration\""

# Local Development
db:
	docker compose run --service-ports -d postgres_db 

run:
	docker compose up

# Host API locally, loading local env file
local_server:
	source $(VENV_DIR)/bin/activate && \
	uvicorn app.adaptor.into.api.app:app --reload --env-file environment/local.env

# Testing commands
pytest:
	@echo "Running unit tests"
	. $(VENV_DIR)/bin/activate; \
	pytest

db_test_start:
	docker compose run --service-ports -d postgres_db_test
	docker compose run --service-ports -d firestore_emulator

db_test_stop:
	docker compose stop postgres_db_test firestore_emulator

coverage:
	@echo "Running unit tests"	
	. $(VENV_DIR)/bin/activate; \
	pytest --cov-report html	

lint:
	@echo "Linting"
	. $(VENV_DIR)/bin/activate; \
	black python/
	flake8 python/

clean:
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

check_for_sa_creds:
	[ -f creds.json ] || \
	(gcloud auth application-default login && \
	export GCP_PROJECT_NUMBER=574107810202 && \
	python python/tooling/get_sa_creds_file.py)

save_docs:
	# Note: requires server to be running locally
	curl http://127.0.0.1:8000/openapi.json -o openapi.json

migrate_firestore_data:
	(gcloud auth application-default login && \
	export FF_ENABLE_FIRESTORE=true && \
	python python/tooling/migrate_firestore_data.py)
	
