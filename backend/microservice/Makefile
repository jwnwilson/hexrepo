.PHONY: venv_setup test lint

.DEFAULT_GOAL = help

run: db_upgrade local_server
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

