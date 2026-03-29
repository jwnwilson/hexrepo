.PHONY: venv run run-cheap run-search run-review run-prep run-search-cheap run-review-cheap run-prep-cheap lint clean help
.DEFAULT_GOAL = help
.EXPORT_ALL_VARIABLES:

VENV := .venv
MKFILE_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
VENV_DIR = $(MKFILE_DIR)$(VENV)

# Load .env if it exists
-include .env
export

# Setup

venv: ## Install dependencies
	@../../tools/bash_scripts/setup_env.sh

# Full pipeline

run: venv ## Run full pipeline (opus, full scope)
	uv run python main.py

run-cheap: venv ## Run full pipeline (haiku, reduced scope — for testing)
	uv run python main.py --cheap

# Individual stages — full

run-search: venv ## Stage 1: search for job candidates
	uv run python main.py --stage search

run-review: venv ## Stage 2: validate and rank candidates
	uv run python main.py --stage review

run-prep: venv ## Stage 3: generate tailored prep materials (top 5)
	uv run python main.py --stage prep

# Individual stages — cheap

run-search-cheap: venv ## Stage 1 (cheap): search for job candidates
	uv run python main.py --stage search --cheap

run-review-cheap: venv ## Stage 2 (cheap): validate and rank candidates
	uv run python main.py --stage review --cheap

run-prep-cheap: venv ## Stage 3 (cheap): generate prep materials (top 1)
	uv run python main.py --stage prep --cheap

# Dev

lint: ## Run ruff linter
	uv run ruff check .

lint-fix: ## Run ruff linter with auto-fix
	uv run ruff check . --fix

clean: ## Remove cache files and output
	@find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	@rm -rf output/

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'
