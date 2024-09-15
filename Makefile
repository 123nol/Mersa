VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
DJANGO = $(PYTHON) manage.py

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make install      Install dependencies"
	@echo "  make migrate      Apply database migrations"
	@echo "  make makemigrations  Create new migrations based on changes"
	@echo "  make run          Start the Django development server"
	@echo "  make test         Run tests"
	@echo "  make lint         Run linting"
	@echo "  make shell        Open Django shell"
	@echo "  make clean        Remove Python bytecode and other artifacts"

.PHONY: venv
venv:
	python3 -m venv venv

.PHONY: install
install:
	$(PIP) install -r requirements.txt

.PHONY: makemigrations
makemigrations:
	$(DJANGO) makemigrations

.PHONY: migrate
migrate:
	$(DJANGO) migrate

.PHONY: run
run:
	$(DJANGO) runserver localhost:8000

.PHONY: test
test:
	$(DJANGO) test

.PHONY: lint
lint:
	flake8 .

.PHONY: shell
shell:
	$(DJANGO) shell

.PHONY: clean
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf *.egg-info
	rm -rf .tox
	rm -rf .coverage
	rm -rf .nox
	rm -rf .mypy_cache
	rm -rf .pytest_cache

.PHONY: migrate-run
migrate-run: makemigrations migrate run
	@echo "Done!"
