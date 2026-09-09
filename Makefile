PYTHON ?= python

.DEFAULT_GOAL := help

.PHONY: help setup test lint jisdor pilot report-only clean

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  %-14s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Install Python dependencies
	$(PYTHON) -m pip install -r requirements.txt

test: ## Run the offline pytest suite
	$(PYTHON) -m pytest -q

lint: ## Run ruff static checks
	$(PYTHON) -m ruff check .

jisdor: ## Clean and validate the Bank Indonesia JISDOR workbook
	$(PYTHON) -m src.preprocessing.clean_jisdor

pilot: ## Collect and clean the authorized seven-day GDELT pilot (hits the live API)
	$(PYTHON) -m src.acquisition.collect_gdelt --start-date 2021-09-01 --end-date 2021-09-07 --pilot

report-only: ## Rebuild pilot QA offline from retained checkpoints (no HTTP)
	$(PYTHON) -m src.acquisition.collect_gdelt --pilot --report-only

clean: ## Remove pytest/ruff caches and __pycache__ dirs (never touches data/)
	rm -rf .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
