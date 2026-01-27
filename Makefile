PYTHON_VENV := .venv
UVICORN_CMD := uvicorn main:app --reload --port 8000
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

test: ## Run tests using pycefr_test.db
	@echo "Running tests..."
	@export DATABASE_PATH=database/pycefr_test.db && $(PYTHON_VENV)/bin/pytest tests/ -v


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

seed: ## Wipe data and fill database with test data (initialize_db.sql)
	@echo "Seeding database with test data..."
	@if [ ! -f "$(DB_SQLITE_PATH)" ]; then \
		echo "Error: Database file not found"; \
		exit 1; \
	fi
	@sqlite3 $(DB_SQLITE_PATH) ".read backend/db/initialize_db.sql"
	@echo "Done"

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