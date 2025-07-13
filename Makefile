# MusicFlow Organizer - Development Automation
# Professional CI/CD pipeline for music library organization tool

.PHONY: help install format lint test security build clean dev

# Default target
help:
	@echo "🎧 MusicFlow Organizer - Development Commands"
	@echo "============================================="
	@echo "install     Install dependencies and development tools"
	@echo "format      Auto-format code (black, isort)"
	@echo "lint        Run all linters (flake8, mypy, pydocstyle)"
	@echo "test        Run test suite with coverage"
	@echo "security    Run security scans (bandit, safety)"
	@echo "qa          Run complete quality assurance pipeline"
	@echo "build       Build distribution packages"
	@echo "clean       Clean build artifacts"
	@echo "dev         Setup development environment"
	@echo "ci-check    Run all CI checks (format, lint, test, security)"

# Installation and setup
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	pip install -e .
	@echo "🔧 Installing development tools..."
	pip install black isort flake8 mypy bandit safety pytest-cov pre-commit
	pre-commit install

dev: install
	@echo "🚀 Setting up development environment..."
	@echo "✅ Development environment ready!"

# Code formatting
format:
	@echo "🎨 Formatting code..."
	black src/ --line-length=100
	black *.py --line-length=100
	isort src/ --profile=black --line-length=100
	isort *.py --profile=black --line-length=100
	@echo "✅ Code formatting complete"

# Linting and static analysis
lint:
	@echo "🔍 Running linters..."
	@echo "Running flake8..."
	flake8 src/ --max-line-length=100 --ignore=E203,W503,D100,D101,D102,D103
	flake8 *.py --max-line-length=100 --ignore=E203,W503,D100,D101,D102,D103
	@echo "Running mypy..."
	mypy src/ --ignore-missing-imports --no-strict-optional
	@echo "Running pydocstyle..."
	pydocstyle src/ --convention=google --add-ignore=D100,D101,D102,D103
	@echo "✅ Linting complete"

# Testing
test:
	@echo "🧪 Running test suite..."
	pytest -v --cov=src --cov-report=html --cov-report=term-missing
	@echo "Running integration tests..."
	python test_app.py
	@echo "✅ Testing complete"

# Security scanning
security:
	@echo "🔒 Running security scans..."
	@echo "Running bandit..."
	bandit -r src/ -f json -o bandit-report.json || true
	bandit -r src/ --severity-level medium
	@echo "Running safety check..."
	safety check --json --output safety-report.json || true
	safety check
	@echo "✅ Security scanning complete"

# Complete QA pipeline
qa: format lint test security
	@echo "🎯 Quality Assurance Pipeline Complete"
	@echo "======================================="
	@echo "✅ Code formatted and linted"
	@echo "✅ Tests passed with coverage"
	@echo "✅ Security checks completed"
	@echo "🏆 Ready for production!"

# CI/CD checks
ci-check:
	@echo "🚀 Running CI checks..."
	@echo "1/4 - Checking code format..."
	black --check src/ *.py --line-length=100
	isort --check-only src/ *.py --profile=black --line-length=100
	@echo "2/4 - Running linters..."
	flake8 src/ *.py --max-line-length=100 --ignore=E203,W503,D100,D101,D102,D103
	mypy src/ --ignore-missing-imports --no-strict-optional
	@echo "3/4 - Running tests..."
	pytest --cov=src --cov-fail-under=70
	@echo "4/4 - Security checks..."
	bandit -r src/ --severity-level medium
	@echo "✅ All CI checks passed!"

# Build and distribution
build: qa
	@echo "📦 Building distribution..."
	python -m build
	@echo "✅ Build complete"

# Cleanup
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleanup complete"

# Performance profiling
profile:
	@echo "⚡ Running performance analysis..."
	python -m cProfile -o profile_stats.prof main.py
	@echo "✅ Profile saved to profile_stats.prof"

# Documentation generation
docs:
	@echo "📚 Generating documentation..."
	sphinx-apidoc -o docs/ src/
	@echo "✅ Documentation generated"