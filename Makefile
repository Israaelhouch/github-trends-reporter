.PHONY: install test lint format run run-offline ai-setup docker-up docker-down docker-clean

PY ?= .venv/bin/python

install:  ## Create .venv and install dev dependencies
	python3 -m venv .venv
	$(PY) -m pip install -r requirements-dev.txt

test:  ## Run the test suite
	$(PY) -m pytest

lint:  ## Lint and check formatting
	$(PY) -m ruff check .
	$(PY) -m ruff format --check .

format:
	$(PY) -m ruff check --fix .
	$(PY) -m ruff format .

run:  ## Run the full pipeline locally (uses Ollama if it's running)
	$(PY) main.py

run-offline:  ## Run without the AI and email steps
	$(PY) main.py --no-ai --no-email

ai-setup:  ## Download the default open model for the AI summary (~2 GB, needs Ollama)
	ollama pull $${AI_MODEL:-qwen2.5:3b}

docker-up:  ## Run once against PostgreSQL in Docker
	docker compose up --build --abort-on-container-exit --exit-code-from app

docker-down:
	docker compose down

docker-clean:  ## Also delete the PostgreSQL volume
	docker compose down --volumes
