.PHONY: venv test lint
.DEFAULT_GOAL = help
.EXPORT_ALL_VARIABLES:

VENV := .venv
MKFILE_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
VENV_DIR = $(MKFILE_DIR)$(VENV)

# Setup commands
venv:
	@../../../tools/bash_scripts/setup_env.sh

test: db venv
	@echo "Running tests..."
	@../../../tools/bash_scripts/test.sh

# Setup docker db for tests
db: down
	docker compose up -d

down:
	docker compose down

coverage:
	@echo "Running unit tests"	
	. $(VENV_DIR)/bin/activate; \
	pytest --cov-report html	

lint: venv
	@TARGET_DIRS="hexrepo_db tests" bash ../../../tools/bash_scripts/lint.sh 

lint_check: venv
	@TARGET_DIRS="hexrepo_db tests" bash ../../../tools/bash_scripts/lint.sh --check

clean:
	@find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

publish: venv
	@echo "Publishing package..."
	@../../../tools/bash_scripts/publish.sh
