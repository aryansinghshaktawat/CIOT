# Makefile for CIOT Development

.PHONY: help install install-dev test test-cov lint format clean run build upload docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black and isort"
	@echo "  clean        Clean build artifacts"
	@echo "  run          Run the application"
	@echo "  build        Build distribution packages"
	@echo "  upload       Upload to PyPI (requires credentials)"
	@echo "  docs         Build documentation"
	@echo "  security     Run security checks"

# Installation targets
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

# Testing targets
test:
	python -m pytest tests/

test-cov:
	python -m pytest --cov=src --cov-report=html --cov-report=term tests/

# Code quality targets
lint:
	flake8 src/ tests/
	mypy src/
	bandit -r src/

format:
	black src/ tests/
	isort src/ tests/

# Security checks
security:
	bandit -r src/
	safety check

# Cleaning targets
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Application targets
run:
	python ciot.py

# Build targets
build: clean
	python -m build

upload: build
	python -m twine upload dist/*

# Documentation targets
docs:
	cd docs && make html

# Development setup
setup-dev: install-dev
	pre-commit install

# All checks (for CI)
check: lint test security

# Quick development cycle
dev: format lint test