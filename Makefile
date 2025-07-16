.PHONY: build install install-dev install-docs test format lint security docs clean help

POETRY := poetry

help:
	@echo "Available targets:"
	@echo "  build        - Build the package"
	@echo "  install      - Install the package and dependencies"
	@echo "  install-dev  - Install the package and dev dependencies"
	@echo "  test         - Run tests"
	@echo "  format       - Format code with black"
	@echo "  lint         - Run linting checks"
	@echo "  security     - Run security checks with bandit"
	@echo "  docs         - Build the documentation"
	@echo "  clean        - Clean build artifacts and cache"
	@echo "  help         - Show this help message"

build: install-dev
	$(POETRY) build

install:
	$(POETRY) install

install-dev:
	which $(POETRY) || pip install poetry
	$(POETRY) install --with dev

install-docs: install-dev
	$(POETRY) install --with dev,docs

install-test: install-dev
	@if [ ! -f ./test-data/zot ]; then \
		if [ "$(shell uname)" = "Darwin" ] && [ "$(shell uname -m)" = "arm64" ]; then \
			curl -L -o ./test-data/zot https://github.com/project-zot/zot/releases/download/v2.1.0/zot-darwin-arm64; \
		elif [ "$(shell uname)" = "Linux" ] && [ "$(shell uname -m)" = "x86_64" ]; then \
			curl -L -o ./test-data/zot https://github.com/project-zot/zot/releases/download/v2.1.0/zot-linux-amd64; \
		else \
			echo "Unsupported platform or architecture"; \
			exit 1; \
		fi; \
	fi
	chmod +x ./test-data/zot
	rm -rf test-data/gardenlinux
	git submodule update --init --recursive

test: install-test
	$(POETRY) run pytest -k "not kms"

test-coverage: install-test
	$(POETRY) run pytest -k "not kms" --cov=gardenlinux --cov-report=xml tests/

test-coverage-ci: install-test
	$(POETRY) run pytest -k "not kms" --cov=gardenlinux --cov-report=xml --cov-fail-under=50 tests/

test-debug: install-test
	$(POETRY) run pytest -k "not kms" -vvv -s

test-trace: install-test
	$(POETRY) run pytest -k "not kms" -vvv --log-cli-level=DEBUG

format: install-dev
	$(POETRY) run black --extend-exclude test-data/gardenlinux .

lint: install-dev
	$(POETRY) run black --check --extend-exclude test-data/gardenlinux .

security: install-dev
	@if [ "$(CI)" = "true" ]; then \
		$(POETRY) run bandit -ll -ii -r . -f json -o bandit-report.json ; \
	else \
		$(POETRY) run bandit -r . ; \
	fi

docs: install-docs
	$(POETRY) run sphinx-build docs _build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .eggs/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	rm -rf test-data/zot
	cd test-data/gardenlinux && git reset --hard
