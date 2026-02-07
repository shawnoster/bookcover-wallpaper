.PHONY: help install dev test lint check run clean build

help:  ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync

dev:  ## Install dependencies including dev tools
	uv sync --all-groups

test:  ## Run tests
	uv run pytest -v

test-cov:  ## Run tests with coverage
	uv run pytest --cov=bookcover_wallpaper --cov-report=term-missing

lint:  ## Run type checking with mypy
	uv run mypy src/

check: lint test  ## Run both linting and tests

run:  ## Run the CLI with --help
	uv run bookcover-wallpaper --help

example-local:  ## Run example with local source (requires --path)
	@echo "Usage: make example-local PATH=/path/to/covers"
	@if [ -z "$(PATH)" ]; then \
		echo "Error: PATH not set"; \
		exit 1; \
	fi
	uv run bookcover-wallpaper --source local --path $(PATH)

example-goodreads:  ## Run example with Goodreads source (requires CSV=/path/to/csv)
	@echo "Usage: make example-goodreads CSV=/path/to/goodreads.csv"
	@if [ -z "$(CSV)" ]; then \
		echo "Error: CSV not set"; \
		exit 1; \
	fi
	uv run bookcover-wallpaper --source goodreads --goodreads-csv $(CSV)

example-search:  ## Run example with search source
	uv run bookcover-wallpaper --source search --query "best fantasy books" --genre fantasy --limit 15

build:  ## Build the package
	uv build

clean:  ## Clean up cache files and build artifacts
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete

cache-clean:  ## Clean the cover cache directory
	rm -rf ~/.cache/bookcover-wallpaper/

.DEFAULT_GOAL := help
