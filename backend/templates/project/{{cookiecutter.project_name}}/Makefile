.PHONY: venv test lint
.DEFAULT_GOAL = help
.EXPORT_ALL_VARIABLES:

TF_VAR_docker_tag=${docker_tag}
TF_VAR_environment=${environment}
{ % if cookiecutter.cloud_provider == 'aws' %}
TF_VAR_ecr_api_url=${AWS_ACCOUNT}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/{{cookiecutter.project_slug}}_api
TF_VAR_aws_access_key=${AWS_ACCESS_KEY_ID}
TF_VAR_aws_secret_key=${AWS_SECRET_ACCESS_KEY}
TF_VAR_aws_region=${AWS_DEFAULT_REGION}
{ % endif %}

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

build:
	docker compose build 

# DB management
db_delete_data: down
	docker compose run postgres_db bash -c "rm -rf /var/lib/postgresql/data/*"

db_upgrade: down
	source $(VENV_DIR)/bin/activate && \
	docker compose run api bash -c "alembic upgrade head"

db_downgrade: down
	docker compose run api bash -c "alembic downgrade -1"

db_create_migration: down
	docker compose run api bash -c "alembic revision --autogenerate -m \"DB migration\""

# Local Development
db:
	docker compose run --service-ports -d postgres_db 

run:
	docker compose up

down:
	docker compose down

# Host API locally, loading local env file
run_local: down db
	source $(VENV_DIR)/bin/activate && \
	PYTHONPATH=src uvicorn app.interactor.api.fastapi.main:app --reload --env-file env/local.env

# Testing commands
test:
	@echo "Running unit tests"
	. $(VENV_DIR)/bin/activate; \
	pytest

coverage:
	@echo "Running unit tests"	
	. $(VENV_DIR)/bin/activate; \
	pytest --cov-report html	

lint:
	bash ./scripts/lint.sh

clean:
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete


tf_init:
	cd infra/tf/{{cookiecutter.cloud_provider}}  && terraform init -input=false

tf_plan:
	cd infra/tf/{{cookiecutter.cloud_provider}}  && terraform plan -out tfapply

tf_apply:
	cd infra/tf/{{cookiecutter.cloud_provider}}  && terraform apply -auto-approve tfapply

tf_destroy:
	cd infra/tf/{{cookiecutter.cloud_provider}}  && terraform destroy
