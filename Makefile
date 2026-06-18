.PHONY: help install dev lint typecheck test clean run setup

help:
	@echo "docintellect-rpa - Comandos:"
	@echo "  make setup      Instala dependencias + configura ambiente"
	@echo "  make run        Sobe API + UI (http://127.0.0.1:8000 + :8501)"
	@echo "  make run-api    Sobe apenas a API"
	@echo "  make run-ui     Sobe apenas a UI"
	@echo "  make lint       Executa ruff"
	@echo "  make typecheck  Executa mypy"
	@echo "  make test       Executa pytest"
	@echo "  make clean      Limpa artefatos"

setup:
	pip install -e ".[dev,ocr,nlp,ui]"
	cp -n .env.example .env 2>/dev/null || true
	@echo "Crie as pastas data/ e logs/ se necessario"

run:
	python run.py

run-api:
	python run.py --no-ui

run-ui:
	python run.py --no-api

install:
	pip install -e .

dev:
	pip install -e ".[dev,ocr,nlp,ui]"

lint:
	ruff check app/ tests/ --fix

typecheck:
	mypy app/

test:
	pytest --cov=app --cov-report=term-missing -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	rm -rf *.egg-info dist build
