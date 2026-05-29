FRONTEND_OUTPUT := frontend-vue/src/client

default: help

# ==============================
# Docker
# ==============================

up: ## Start all services
	docker compose up

build: ## Rebuild Docker images (after dependency changes)
	docker compose build

down: ## Stop all services
	docker compose down

logs: ## Tail Docker logs
	docker compose logs -f

reset: ## Stop services and wipe the database volume
	docker compose down -v

shell: ## Open SQLite interactive shell inside the backend container
	docker compose exec backend sqlite3 /app/database/pycefr.db

seed: ## Seed the database with demo data
	docker compose exec backend python scripts/seed.py

# ==============================
# Quality
# ==============================

format: ## Format backend (ruff) and frontend (prettier)
	docker compose exec backend python -m ruff format .
	docker compose exec frontend npx prettier --write .

test: ## Run backend tests
	docker compose exec backend python -m pytest backend/tests/ -v

lint: lint-back lint-front ## Run all linters

lint-back: ## Run backend linters (ruff + mypy)
	docker compose exec backend python -m ruff check .
	docker compose exec backend python -m mypy .

lint-front: ## Run frontend linters (eslint + vue-tsc)
	docker compose exec frontend npm run lint
	docker compose exec frontend npm run type-check

# ==============================
# Code Generation
# ==============================

gen-ts: ## Regenerate TypeScript client from OpenAPI schema (backend must be running)
	@echo "Generating TypeScript client from OpenAPI schema..."
	@cd frontend-vue && npm run gen-client
	@echo "Done"

# ==============================
# Maintenance
# ==============================

clean: ## Delete generated TypeScript client
	@echo "Cleaning up generated files..."
	rm -rf $(FRONTEND_OUTPUT)/*
	@echo "Cleanup complete."

help: ## Show this help menu
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
