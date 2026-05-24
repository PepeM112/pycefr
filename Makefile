PYTHON_VENV := .venv
UVICORN_CMD := uvicorn main:app --reload --reload-exclude backend/tmp --port 8000
OPENAPI_URL := http://localhost:8000/openapi.json
FRONTEND_OUTPUT := ./src/client
VITE_DEV := npm run dev --prefix frontend
DB_SQLITE_PATH := database/pycefr.db

# ==============================
# Main
# ==============================

default: help

setup: ## Install backend/frontend dependencies and initialize database
	@make install-backend
	@make install-frontend
	@make init-db

run-all: ## Run backend and frontend in parallel with TS generation
	@make backend-in-bg frontend-in-bg gen-ts

# ==============================
# Backend
# ==============================

test: ## Run all backend tests
	@echo "Running tests..."
	@$(PYTHON_VENV)/bin/pytest backend/tests/ -v


install-backend: ## Create virtual environment and install dependencies
	@echo "-> Creating and activating virtual environment..."
	python -m venv $(PYTHON_VENV)
	@echo "-> Installing Python dependencies..."
	$(PYTHON_VENV)/bin/pip install .

up-backend: ## Start FastAPI server with hot-reload
	@echo "Running FastAPI server in http://localhost:8000 ..."
	@$(PYTHON_VENV)/bin/$(UVICORN_CMD) --app-dir backend

# ==============================
# Database
# ==============================

init-db: ## Wipe database and create a fresh one from schema.sql
	@mkdir -p database
	@echo "Initializing SQLite database..."
	@if [ -f "$(DB_SQLITE_PATH)" ]; then rm $(DB_SQLITE_PATH); fi
	@sqlite3 $(DB_SQLITE_PATH) ".read backend/db/schema.sql"
	@echo "Done"

seed: ## Seed database with real analyses from well-known repos (backend must be running)
	@$(PYTHON_VENV)/bin/python scripts/seed.py

db-shell: ## Open SQLite interactive shell
	@sqlite3 $(DB_SQLITE_PATH)

# ==============================
# Frontend
# ==============================

install-frontend: ## Install frontend-vue npm dependencies
	@echo "Installing frontend dependencies..."
	npm install --prefix frontend-vue

up-frontend: ## Start Vite development server
	@echo "Running Vite development server in http://localhost:5173 ..."
	@npm run dev --prefix frontend-vue

gen-ts: ## Generate TypeScript client from OpenAPI/Pydantic models
	@echo "Generating TypeScript client from OpenAPI schema..."
	@cd frontend-vue && npm run gen-client
	@echo "Done"

# ==============================
# Docker
# ==============================

docker-up: ## Start all services with Docker Compose
	docker compose up --build -d

docker-down: ## Stop Docker services
	docker compose down

docker-seed: ## Seed the Docker database with demo data
	docker compose exec backend python scripts/seed.py

docker-logs: ## Tail Docker logs
	docker compose logs -f

# ==============================
# Maintenance
# ==============================

clean: ## Delete virtual environment, generated clients, and database
	@echo "Cleaning up generated files..."
	rm -rf $(PYTHON_VENV)
	rm -rf $(FRONTEND_OUTPUT)/*
	rm -f $(DB_SQLITE_PATH)
	@echo "Cleanup complete."

help: ## Show this help menu
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'