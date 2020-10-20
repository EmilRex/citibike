SHELL := /bin/bash

install:
	pip install .

compose:
	docker-compose up

run:
	@echo "Waiting for postgres to come online..."
	sleep 10
	@echo "Running migrations..."
	alembic upgrade head
	@echo "Running citibike..."
	python citibike/pipeline.py

test:
	pip install pytest==4.3.1
	pytest -v .

clean:
	find . -name '.DS_STORE' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -fr .pytest_cache/

.PHONY: install compose run test clean