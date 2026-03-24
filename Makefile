PYTHON := apps/api/.venv/bin/python

# ── Setup ────────────────────────────────────────────────────────────────────

.PHONY: setup
setup: ## Install all dependencies (run once after cloning)
	python3 -m venv apps/api/.venv
	apps/api/.venv/bin/pip install -r apps/api/requirements-dev.txt
	pnpm install

# ── Local dev ────────────────────────────────────────────────────────────────

.PHONY: services up down
services: ## Start Postgres + Redis in the background
	docker compose up -d

up: services ## Alias for services

down: ## Stop Postgres + Redis
	docker compose down

.PHONY: api web
api: ## Run the FastAPI dev server
	cd apps/api && ../.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

web: ## Run the Next.js dev server
	pnpm --filter web dev

# ── Database ─────────────────────────────────────────────────────────────────

.PHONY: migrate migration
migrate: ## Apply all pending migrations
	cd apps/api && ../.venv/bin/alembic upgrade head

migration: ## Create a new migration (usage: make migration name="add users table")
	cd apps/api && ../.venv/bin/alembic revision --autogenerate -m "$(name)"

# ── Testing ──────────────────────────────────────────────────────────────────

.PHONY: test test-cov
test: ## Run API tests
	$(PYTHON) -m pytest apps/api/tests

test-cov: ## Run API tests with coverage report
	$(PYTHON) -m pytest apps/api/tests --cov=apps/api/app --cov-report=term-missing

# ── Lint & typecheck ─────────────────────────────────────────────────────────

.PHONY: lint typecheck format
lint: ## Lint all code
	apps/api/.venv/bin/ruff check apps/api
	pnpm --filter web lint

typecheck: ## Typecheck the web app
	pnpm --filter web typecheck

format: ## Format all TS/TSX files with Prettier
	pnpm format

# ── Help ─────────────────────────────────────────────────────────────────────

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
