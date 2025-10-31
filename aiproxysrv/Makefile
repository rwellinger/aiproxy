# Makefile for aiproxysrv development tasks

.PHONY: help lint lint-ruff lint-imports lint-all format test install-dev

# Default target
help:
	@echo "Available targets:"
	@echo "  lint-ruff      - Run Ruff linter (code quality)"
	@echo "  lint-imports   - Run import-linter (architecture validation)"
	@echo "  lint-all       - Run all linters (Ruff + import-linter)"
	@echo "  format         - Format code with Ruff"
	@echo "  test           - Run pytest"
	@echo "  install-dev    - Install development dependencies"

# Ruff linting
lint-ruff:
	@echo "Running Ruff linter..."
	ruff check .

# Architecture validation
lint-imports:
	@echo "Running import-linter (architecture validation)..."
	lint-imports

# Run all linters
lint-all: lint-ruff lint-imports
	@echo "All linters passed!"

# Format code
format:
	@echo "Formatting code with Ruff..."
	ruff check . --fix
	ruff format .

# Run tests
test:
	@echo "Running pytest..."
	pytest -v

# Install development dependencies
install-dev:
	@echo "Installing development dependencies..."
	pip install -e ".[dev,test]"
