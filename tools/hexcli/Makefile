.PHONY: venv
.DEFAULT_GOAL = help
.EXPORT_ALL_VARIABLES:

VENV=.venv
VENV_DIR = $(MKFILE_DIR)$(VENV)

# Setup commands
venv:
	@echo "Checking if venv is setup..."
	@../bash_scripts/setup_env.sh

# Testing commands
test: venv
	@echo "Running unit tests"
	. $(VENV_DIR)/bin/activate; \
	pytest