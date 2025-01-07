.PHONY: venv test lint
.DEFAULT_GOAL = help
.EXPORT_ALL_VARIABLES:

TF_VAR_docker_tag := latest
TF_VAR_environment=${ENVIRONMENT}
TF_VAR_ecr_api_url=${AWS_ACCOUNT}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/monitor_api
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
db_migrate:
	bash -c "source $(VENV_DIR)/bin/activate && alembic upgrade head" ;\
	EXIT_CODE=$$?;\
    exit $$EXIT_CODE

db_migrate_docker:
	docker compose run api bash -c "alembic upgrade head"

db_delete_data: down
	docker compose run postgres_db bash -c "rm -rf /var/lib/postgresql/data/*"

db_upgrade: db_migrate down

db_downgrade: down
	bash -c "source $(VENV_DIR)/bin/activate && alembic downgrade -1"

db_create_migration: down
	bash -c "source $(VENV_DIR)/bin/activate && alembic revision --autogenerate -m \"DB migration\""

db:
	docker compose run --service-ports -d postgres_db 

down:
	docker compose down

# Local Development

# Host API locally, loading local env file
run: down db venv
	source $(VENV_DIR)/bin/activate && \
	PYTHONPATH=src uvicorn app.interactor.api.fastapi.main:app --reload --env-file env/local.env

# Host API locally, connect to cloud db. Still requires manual setting of DB_PASSWORD_SECRET_NAME in bastion.env
run_bastion: bastion venv
	source $(VENV_DIR)/bin/activate && \
	PYTHONPATH=src uvicorn app.interactor.api.fastapi.main:app --reload --env-file env/local.env

# Host API locally and run in docker
run_docker:
	docker compose up

# Testing commands
test: venv
	@echo "Running unit tests"
	. $(VENV_DIR)/bin/activate; \
	pytest

coverage:
	@echo "Running unit tests"	
	. $(VENV_DIR)/bin/activate; \
	pytest --cov-report html	

lint:
	@TARGET_DIRS="src" bash ../../tools/bash_scripts/lint.sh 

lint_check: venv
	@TARGET_DIRS="src" bash ../../tools/bash_scripts/lint.sh --check

clean:
	@find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

tf_workspace:
	@cd infra/tf/aws/environment  && \
	terraform workspace select -or-create=true $(ENVIRONMENT) 

tf_init:
	@echo "Initializing Terraform infra"
	cd infra/tf/aws/shared  && terraform init -input=false
	cd infra/tf/aws/environment  && terraform init -input=false

tf_setup: tf_init
	@echo "Applying Inital project Terraform infra"
	cd infra/tf/aws/shared && terraform workspace select -or-create=true default
	cd infra/tf/aws/shared && terraform apply

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
	PROJECT=monitor NO_INPUT=$(NO_INPUT) ENVIRONMENT=$(ENVIRONMENT) ../../tools/bash_scripts/deploy.sh 

bastion: venv
	@echo "Activating bastion port forwarding..."
	cd ../../ && \
	hextech bastion 