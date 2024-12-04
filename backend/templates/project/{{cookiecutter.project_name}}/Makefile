.PHONY: venv test lint
.DEFAULT_GOAL = help
.EXPORT_ALL_VARIABLES:

TF_VAR_docker_tag=${docker_tag}
TF_VAR_environment=${ENVIRONMENT}
{% if cookiecutter.cloud_provider == 'aws' %}
TF_VAR_ecr_api_url=${AWS_ACCOUNT}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/{{cookiecutter.project_slug}}_api
TF_VAR_aws_access_key=${AWS_ACCESS_KEY_ID}
TF_VAR_aws_secret_key=${AWS_SECRET_ACCESS_KEY}
TF_VAR_aws_region=${AWS_DEFAULT_REGION}
{% endif %}

VENV := .venv
MKFILE_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
VENV_DIR = $(MKFILE_DIR)$(VENV)

# Setup commands
venv:
	@echo "Checking if venv is setup..."
	@./tools/setup_env.sh

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
run_local: down db venv
	source $(VENV_DIR)/bin/activate && \
	PYTHONPATH=src uvicorn app.interactor.api.fastapi.main:app --reload --env-file env/local.env

# Testing commands
test: venv
	@echo "Running unit tests"
	. $(VENV_DIR)/bin/activate; \
	pytest

coverage:
	@echo "Running unit tests"	
	. $(VENV_DIR)/bin/activate; \
	pytest --cov-report html	

lint: venv
	bash ./tools/lint.sh

lint_check: venv
	bash ./tools/lint.sh --check

clean:
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

tf_workspace:
	@cd infra/tf/{{cookiecutter.cloud_provider}}/environment  && terraform workspace new $(ENVIRONMENT)

tf_init:
	@echo "Initializing Terraform infra"
	cd infra/tf/{{cookiecutter.cloud_provider}}/shared  && terraform init -input=false
	cd infra/tf/{{cookiecutter.cloud_provider}}/environment  && terraform init -input=false

tf_plan:
	@echo "Planning Terraform infra"
	cd infra/tf/{{cookiecutter.cloud_provider}}/shared  && terraform plan -out tfapply
	cd infra/tf/{{cookiecutter.cloud_provider}}/environment  && terraform plan -out tfapply

tf_apply:
	@echo "Applying Terraform infra"
	cd infra/tf/{{cookiecutter.cloud_provider}}/shared  && terraform apply
	cd infra/tf/{{cookiecutter.cloud_provider}}/environment  && terraform apply

tf_destroy:
	@echo "Destroying Terraform infra"
	cd infra/tf/{{cookiecutter.cloud_provider}}/environment  && terraform destroy
	cd infra/tf/{{cookiecutter.cloud_provider}}/shared  && terraform destroy

tf_setup:
	@echo "Applying Terraform infra"
	cd infra/tf/aws/shared && terraform apply
	@echo "Deploying image to enable environment deployment"
	./tools/deploy.sh
	cd infra/tf/aws/environment  && terraform apply

deploy_container:
	./tools/deploy.sh