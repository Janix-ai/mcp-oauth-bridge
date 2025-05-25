.PHONY: help install install-dev test lint format type-check clean build publish-test publish docs

help:		## Show this help
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:	## Install package for production
	pip install .

install-dev:	## Install package for development
	pip install -e ".[dev,test]"
	pre-commit install

test:		## Run tests
	pytest tests/ -v --cov=mcp_oauth_bridge --cov-report=html --cov-report=term

test-fast:	## Run tests without coverage
	pytest tests/ -v

lint:		## Run all linting tools
	black --check mcp_oauth_bridge tests
	isort --check-only mcp_oauth_bridge tests
	flake8 mcp_oauth_bridge tests
	bandit -r mcp_oauth_bridge

format:		## Format code
	black mcp_oauth_bridge tests
	isort mcp_oauth_bridge tests

type-check:	## Run type checking
	mypy mcp_oauth_bridge

quality:	## Run all quality checks
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test

clean:		## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:		## Build package
	python -m build

check-build:	## Check built package
	twine check dist/*

publish-test:	## Publish to TestPyPI
	$(MAKE) clean
	$(MAKE) build
	$(MAKE) check-build
	twine upload --repository testpypi dist/*

publish:	## Publish to PyPI (use with caution!)
	$(MAKE) clean
	$(MAKE) build
	$(MAKE) check-build
	@echo "Are you sure you want to publish to PyPI? This action cannot be undone."
	@echo "Press Ctrl+C to cancel or Enter to continue..."
	@read
	twine upload dist/*

docs:		## Generate documentation
	@echo "Documentation generation not yet implemented"

bump-patch:	## Bump patch version
	bump2version patch

bump-minor:	## Bump minor version
	bump2version minor

bump-major:	## Bump major version
	bump2version major

release:	## Create a release (runs quality checks first)
	$(MAKE) quality
	$(MAKE) clean
	$(MAKE) build
	@echo "Release artifacts built successfully!"
	@echo "Next steps:"
	@echo "1. Create a git tag: git tag v$(shell python -c 'import mcp_oauth_bridge; print(mcp_oauth_bridge.__version__)')"
	@echo "2. Push the tag: git push origin v$(shell python -c 'import mcp_oauth_bridge; print(mcp_oauth_bridge.__version__)')"
	@echo "3. Create a GitHub release from the tag"
	@echo "4. The CI pipeline will automatically publish to PyPI"

dev-setup:	## Set up development environment
	python -m venv .venv
	@echo "Virtual environment created. Activate with:"
	@echo "source .venv/bin/activate  # Linux/macOS"
	@echo ".venv\\Scripts\\activate     # Windows"
	@echo "Then run: make install-dev" 