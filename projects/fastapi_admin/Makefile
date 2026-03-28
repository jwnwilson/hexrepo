.PHONY: venv test lint
.DEFAULT_GOAL = help
.EXPORT_ALL_VARIABLES:

TF_VAR_docker_tag := latest
TF_VAR_environment=${ENVIRONMENT}
TF_VAR_ecr_api_url=${AWS_ACCOUNT}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/common_api
TF_VAR_aws_access_key=${AWS_ACCESS_KEY_ID}
TF_VAR_aws_secret_key=${AWS_SECRET_ACCESS_KEY}
TF_VAR_aws_region=${AWS_DEFAULT_REGION}

VENV := .venv
MKFILE_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
VENV_DIR = $(MKFILE_DIR)$(VENV)
TARGETS := ${TARGETS}

# Setup commands
venv:
	@../../tools/bash_scripts/setup_env.sh

build:
	docker compose build

# DB management
db_migrate_pipeline:
	bash -c "ENVIRONMENT=$(ENVIRONMENT) uv run alembic upgrade head" ;\
	EXIT_CODE=$$?;\
    exit $$EXIT_CODE

db: docker_stop
	docker compose run --service-ports -d db 

db_migrate_local:
	bash -c "env $$(cat env/local.env|xargs) uv run alembic upgrade head"

db_migrate_docker:
	docker compose run api sh -c "alembic upgrade head"

db_delete_data:
	docker compose run db sh -c "rm -rf /var/lib/postgresql/data/*"

db_downgrade:
	bash -c "uv run alembic downgrade -1"

db_create_migration:
	bash -c 'read -p "Describe migration: " slug && env $$(cat env/local.env|xargs) uv run alembic revision --autogenerate -m "$$slug"'

docker_stop:
	@-bash -c "docker ps -aq | xargs docker stop | xargs docker rm"

down:
	docker compose down
	bash -c "docker ps -aq | xargs docker stop | xargs docker rm"
	
# Local Development

# Host API locally, loading local env file with all supporting services required
run: docker_stop celery venv
	PYTHONPATH=src ENVIRONMENT=local uv run uvicorn app.interactor.api.fastapi.main:app --reload --env-file env/local.env

# Host API locally, loading local env file without celery to run that locally also
api_local: down db localstack venv
	PYTHONPATH=src ENVIRONMENT=local uv run uvicorn app.interactor.api.fastapi.main:app --reload --env-file env/local.env

# Run celery locally, loading local env file
celery_local: down db localstack venv
	PYTHONPATH=src ENVIRONMENT=local uv run watchmedo auto-restart --directory=./src --pattern="*.py" --recursive -- celery -A app.interactor.event.celery.celery_app worker --loglevel=info

python_cli: venv
	PYTHONPATH=src ENVIRONMENT=local uv run python

celery:
	docker compose up -d celery

localstack:
	docker compose up -d localstack

# Temporal commands
temporal:
	docker compose up -d temporal-admin-tools temporal-ui 

temporal_worker: temporal venv
	@-bash -c "echo waiting for temporal to initialise" && sleep 10
	PYTHONPATH=src uv run python -m app.interactor.event.temporal.worker

temporal_ingestion_workflow: venv
	PYTHONPATH=src uv run python -m app.interactor.cli.trigger_ingestion \
	--input-file "./data/input/test_data_1million_rows.csv"
	--batch-size 100000


# Host API locally, connect to cloud db. Still requires manual setting of DB_PASSWORD_SECRET_NAME in bastion.env
run_bastion: bastion venv
	PYTHONPATH=src uv run uvicorn app.interactor.api.fastapi.main:app --reload --env-file env/local.env

# Host API locally and run in docker
run_docker:
	docker compose up

# Testing commands
test: venv db 
	@echo "Running unit tests"
	uv run pytest

load_test: venv
	@echo "Running load tests"
	PYTHONPATH=src uv run locust -f src/tests/load_test/locust.py

coverage:
	@echo "Running unit tests"	
	uv run pytest --cov-report html	

lint:
	@TARGET_DIRS="src" bash ../../tools/bash_scripts/lint.sh 

lint_check: venv
	@TARGET_DIRS="src" bash ../../tools/bash_scripts/lint.sh --check

clean:
	@find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

tf_workspace:
	@cd infra/tf/aws/environment && \
	terraform workspace select -or-create=true $(ENVIRONMENT) 

tf_init:
	@echo "Initializing Terraform infra"
	@rm -rf ./infra/tf/aws/shared/.terraform
	@rm -rf ./infra/tf/aws/environment/.terraform
	cd infra/tf/aws/shared  && terraform init -input=false -upgrade
	cd infra/tf/aws/environment  && terraform init -input=false -upgrade

tf_setup: tf_init
	@echo "Applying Inital project Terraform infra"
	cd infra/tf/aws/shared && terraform workspace select -or-create=true default
	cd infra/tf/aws/shared && terraform apply

tf_plan:
	@echo "Planning Terraform infra"
	cd infra/tf/aws/shared  && terraform plan
	cd infra/tf/aws/environment && terraform plan $(TARGETS)

tf_apply:
	@echo "Applying Terraform infra"
	cd infra/tf/aws/shared && terraform apply
	cd infra/tf/aws/environment && terraform apply $(TARGETS)

tf_apply_no_input:
	@echo "Applying Terraform infra"
	cd infra/tf/aws/shared && terraform apply -auto-approve 
	cd infra/tf/aws/environment && terraform apply -auto-approve $(TARGETS)

tf_destroy:
	@echo "Destroying Terraform infra"
	cd infra/tf/aws/environment  && terraform destroy $(TARGETS)

tf_refresh: tf_workspace
	@cd infra/tf/aws/environment && terraform refresh

tf_output: tf_workspace
	@cd infra/tf/aws/environment && terraform output -json

deploy:
	hextech deploy-projects $(ENVIRONMENT) --no-input --projects=common

bastion: venv
	@echo "Activating bastion port forwarding..."
	cd ../../ && \
	hextech bastion 

ecs_exec: venv
	@echo "Executing command on ECS task..."
	hextech ecs-exec $(ENVIRONMENT) common "/bin/sh" 

create_user:
	PYTHONPATH=src ENVIRONMENT=$(ENVIRONMENT) uv run python src/app/interactor/cli/create_superuser.py

create_permissions:
	PYTHONPATH=src ENVIRONMENT=$(ENVIRONMENT) uv run python src/app/interactor/cli/create_default_permissions.py
