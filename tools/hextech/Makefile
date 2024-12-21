.PHONY: venv
.DEFAULT_GOAL = help
.EXPORT_ALL_VARIABLES:

VENV=.venv
VENV_DIR = $(MKFILE_DIR)$(VENV)

# Setup commands
venv:
	@../bash_scripts/setup_env.sh

# Testing commands
test: venv
	@echo "Running unit tests"
	. $(VENV_DIR)/bin/activate; \
	pytest

lint:
	@TARGET_DIRS="hextech" bash ../../tools/bash_scripts/lint.sh
