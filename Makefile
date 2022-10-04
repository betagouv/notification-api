SHELL := /bin/bash

APP_VERSION_FILE = app/version.py

## DEVELOPMENT

.PHONY: run-dev
run-dev:
	flask run -p 6011 -h 0.0.0.0

.PHONY: run-celery
run-celery:
	celery \
		-A run_celery.notify_celery worker \
		--pidfile="/tmp/celery.pid" \
		--loglevel=INFO \
		--concurrency=4

.PHONY: run-celery-beat
run-celery-beat:
	celery \
		-A run_celery.notify_celery beat \
		--loglevel=INFO

.PHONY: lint
lint:
	flake8 .

.PHONY: order-check
order-check:
	isort --check-only ./app ./tests

.PHONY: test
test:
	pytest -n4 --maxfail=10

.PHONY: freeze-requirements
freeze-requirements: ## Pin all requirements including sub dependencies into requirements.txt
	pip install --upgrade pip-tools
	pip-compile requirements.in

.PHONY: clean
clean:
	rm -rf node_modules cache target venv .coverage build tests/.cache
