.PHONY: help setup dev-backend dev-frontend test lint clean

help:
	@echo "Available commands:"
	@echo "  make setup         - Install dependencies"
	@echo "  make dev-backend   - Run FastAPI backend"
	@echo "  make dev-frontend  - Run Frontend dev server"
	@echo "  make test          - Run all test suites"
	@echo "  make lint          - Run linters"
	@echo "  make clean         - Clean cache and temp files"

setup:
	python -m pip install -r requirements.txt
	cd frontend && npm install

dev-backend:
	uvicorn backend.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

test:
	pytest tests/
