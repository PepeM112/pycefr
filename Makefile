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

setup: install-backend install-frontend db-init

run-all: backend-in-bg frontend-in-bg gen-ts

# ==============================
# Backend
# ==============================

install-backend:
	@echo "-> Creating and activating virtual environment..."
	python -m venv $(PYTHON_VENV)
	@echo "-> Installing Python dependencies..."
	$(PYTHON_VENV)/bin/pip install .

db-init:
	@mkdir -p database
	@echo "-> Initializing SQLite database..."
	@if [ -f "$(DB_SQLITE_PATH)" ]; then rm $(DB_SQLITE_PATH); fi
	@echo ".read backend/db/schema.sql | sqlite3 $(DB_SQLITE_PATH)"
	sqlite3 $(DB_SQLITE_PATH) ".read backend/db/schema.sql"
	@echo ".read backend/db/initialize_db.sql | sqlite3 $(DB_SQLITE_PATH)"
	sqlite3 $(DB_SQLITE_PATH) ".read backend/db/initialize_db.sql"

db-seed:
	@echo "-> Seeding database with test data..."
	@if [ ! -f "$(DB_SQLITE_PATH)" ]; then \
		echo "Error: Database file not found. Run 'make db-init' instead"; \
		exit 1; \
	fi
	sqlite3 $(DB_SQLITE_PATH) ".read backend/db/initialize_db.sql"
	@echo "-> Seed completed successfully."

up-backend:
	@echo "-> Running FastAPI server in http://localhost:8000 ..."
	@$(PYTHON_VENV)/bin/$(UVICORN_CMD) --app-dir backend

# ==============================
# Frontend
# ==============================

install-frontend:
	@echo "-> Installing frontend dependencies..."
	npm install --prefix frontend-vue

up-frontend:
	@echo "-> Running Vite development server in http://localhost:5173 ..."
	@npm run dev --prefix frontend-vue

gen-ts:
	@echo "-> Generating TypeScript client from OpenAPI schema..."
	@cd frontend-vue && npm run gen-client
	@echo "Done"

# ==============================
# Maintenance
# ==============================
clean:
	@echo "-> Cleaning up generated files..."
	rm -rf $(PYTHON_VENV)
	rm -rf $(FRONTEND_OUTPUT)/*
	rm -f $(DB_SQLITE_PATH)
	@echo "Cleanup complete."

db-init-2:
	@echo "-> Initializing SQLite database at $(DB_SQLITE_PATH)..."
	python scripts/init_db.py
	@echo "Database initialized."

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
