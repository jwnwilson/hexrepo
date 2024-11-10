.PHONY: venv test lint
.DEFAULT_GOAL = help

VENV=.venv
VENV_DIR = $(MKFILE_DIR)$(VENV)

# Setup commands
venv:
	@echo "Creating virtual environment..."
	./tools/setup_env.sh

be_project: venv
	@echo "Creating project..."
	. $(VENV_DIR)/bin/activate; \
	python cli.py create-be-project

be_library: venv
	@echo "Creating library..."
	. $(VENV_DIR)/bin/activate; \
	python cli.py create-be-library

add_be_library: venv
	@echo "Adding library to project..."
	. $(VENV_DIR)/bin/activate; \
	python cli.py add_be_library
