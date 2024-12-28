.PHONY: venv test lint
.DEFAULT_GOAL = help
.EXPORT_ALL_VARIABLES:

TF_VAR_docker_tag := latest
TF_VAR_environment=${ENVIRONMENT}
TF_VAR_ecr_api_url=${AWS_ACCOUNT}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/{{cookiecutter.project_slug}}_api
TF_VAR_aws_access_key=${AWS_ACCESS_KEY_ID}
TF_VAR_aws_secret_key=${AWS_SECRET_ACCESS_KEY}
TF_VAR_aws_region=${AWS_DEFAULT_REGION}

VENV := .venv
MKFILE_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
VENV_DIR = $(MKFILE_DIR)$(VENV)

# Setup commands
venv:
	@../../tools/bash_scripts/setup_env.sh

build:
	docker compose build

# DB management
{% if cookiecutter.use_db == "y" and cookiecutter.use_db_logic == "sql" %}
db_migrate:
	bash -c "uv run alembic upgrade head"

db_migrate_local:
	bash -c "env $$(cat env/local.env|xargs) uv run alembic upgrade head"

db_migrate_docker:
	docker compose run api bash -c "alembic upgrade head"

db_delete_data: down
	docker compose run db bash -c "rm -rf /var/lib/postgresql/data/*"

db_upgrade: db_migrate down

db_downgrade: down
	bash -c "uv run alembic downgrade -1"

db_create_migration: down
	bash -c "uv run alembic revision --autogenerate -m \"DB migration\""
{% elif cookiecutter.use_db == "y" and cookiecutter.use_db_logic == "nosql" %}
db_setup:
	bash -c "DB_URL=http://localhost:8888 uv run python -m app.interactor.cli.create_dynamo_tables"

db_delete_data: down
	docker compose run db bash -c "rm -rf /home/dynamodblocal/data/*"
{% endif %}

db:
	docker compose run --service-ports -d db 

down:
	docker compose down

# Local Development

# Host API locally, loading local env file
run: down db venv
	PYTHONPATH=src uv run uvicorn app.interactor.api.fastapi.main:app --reload --env-file env/local.env

# Host API locally, connect to cloud db. Still requires manual setting of DB_PASSWORD_SECRET_NAME in bastion.env
run_bastion: bastion venv
	PYTHONPATH=src uv run uvicorn app.interactor.api.fastapi.main:app --reload --env-file env/local.env

# Host API locally and run in docker
run_docker:
	docker compose up

# Testing commands
{% if cookiecutter.use_db == "y"%}
test: venv db
{% else %}
test: venv
{% endif %}
	@echo "Running unit tests"
	uv run pytest

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
	@-cd infra/tf/aws/environment  && \
	terraform workspace new $(ENVIRONMENT)
	@cd infra/tf/aws/environment  && \
	terraform workspace select $(ENVIRONMENT) 

tf_init:
	@echo "Initializing Terraform infra"
	cd infra/tf/aws/shared  && terraform init -input=false
	cd infra/tf/aws/environment  && terraform init -input=false

tf_setup:
	@echo "Applying Terraform infra"
	cd infra/tf/aws/shared && terraform apply
	@echo "Deploying image to enable environment deployment"
	make deploy

tf_plan:
	@echo "Planning Terraform infra"
	cd infra/tf/aws/shared  && terraform plan
	cd infra/tf/aws/environment && terraform plan

tf_apply:
	@echo "Applying Terraform infra"
	cd infra/tf/aws/shared && terraform apply
	cd infra/tf/aws/environment  && terraform apply

tf_apply_no_input:
	@echo "Applying Terraform infra"
	cd infra/tf/aws/shared && terraform apply -auto-approve
	cd infra/tf/aws/environment && terraform apply -auto-approve

tf_destroy:
	@echo "Destroying Terraform infra"
	cd infra/tf/aws/environment  && terraform destroy
	cd infra/tf/aws/shared  && terraform destroy

deploy: build tf_workspace
	PROJECT={{cookiecutter.project_slug}} NO_INPUT=$(NO_INPUT) ENVIRONMENT=$(ENVIRONMENT) ../../tools/bash_scripts/deploy.sh 

bastion: venv
	@echo "Activating bastion port forwarding..."
	cd ../../ && \
	hextech bastion 